from enum import Enum
from datetime import datetime


class LampType(Enum):
    СВЕТОДИОДНАЯ = 1
    ГАЛОГЕННАЯ = 2
    ЛЮМИНЕСЦЕНТНАЯ = 3
    ЛАМПА_НАКАЛИВАНИЯ = 4


class ProtectionClass(Enum):
    IP20 = 1
    IP40 = 2
    IP44 = 3
    IP54 = 4
    IP65 = 5


class LightingFixture:
    def __init__(self):
        self.model = ""
        self.lamp_type = None
        self.power = 0.0
        self.luminous_flux = 0.0
        self.color_temp = 0
        self.cri = 0.0
        self.protection = None
        self.operating_temp = (0, 0)
        self.lifetime = 0

    def input_parameters(self):
        print("\n=== Ввод параметров осветительного прибора ===")
        self.model = input("Введите модель прибора: ").strip()
        self.lamp_type = self._input_enum("Выберите тип лампы:", LampType)
        self.power = self._input_float("Введите мощность (Вт): ", min_val=0.1)
        self.luminous_flux = self._input_float("Введите световой поток (лм): ", min_val=0.1)
        self.color_temp = self._input_int("Введите цветовую температуру (K, 2400-6500): ", 2400, 6500)
        self.cri = self._input_float("Введите индекс цветопередачи (CRI, 0-100): ", 0, 100)
        self.protection = self._input_enum("Выберите класс защиты:", ProtectionClass)

        print("Введите рабочий температурный диапазон:")
        temp_min = self._input_int("  Минимальная температура (°C): ", -60, 60)
        temp_max = self._input_int("  Максимальная температура (°C): ", temp_min, 100)
        self.operating_temp = (temp_min, temp_max)
        self.lifetime = self._input_int("Введите срок службы (часы): ", min_val=100)

    def _input_float(self, prompt, min_val=None, max_val=None):
        while True:
            try:
                value = float(input(prompt))
                if min_val is not None and value < min_val:
                    print(f"Значение должно быть не менее {min_val}")
                    continue
                if max_val is not None and value > max_val:
                    print(f"Значение должно быть не более {max_val}")
                    continue
                return value
            except ValueError:
                print("Ошибка: введите число")

    def _input_int(self, prompt, min_val=None, max_val=None):
        while True:
            try:
                value = int(input(prompt))
                if min_val is not None and value < min_val:
                    print(f"Значение должно быть не менее {min_val}")
                    continue
                if max_val is not None and value > max_val:
                    print(f"Значение должно быть не более {max_val}")
                    continue
                return value
            except ValueError:
                print("Ошибка: введите целое число")

    def _input_enum(self, prompt, enum_class):
        print(prompt)
        for item in enum_class:
            print(f"{item.value}. {item.name.replace('_', ' ')}")
        while True:
            try:
                choice = int(input("Выберите номер: "))
                return list(enum_class)[choice - 1]
            except (ValueError, IndexError):
                print(f"Ошибка: введите число от 1 до {len(list(enum_class))}")

    def get_unique_id(self):
        return hash((
            self.model.lower(),
            self.lamp_type,
            round(self.power, 2),
            round(self.luminous_flux, 2),
            self.color_temp,
            round(self.cri, 1),
            self.protection,
            self.operating_temp,
            self.lifetime
        ))


class GOSTChecker:
    def __init__(self, fixture):
        self.fixture = fixture
        self.results = {
            'Требования безопасности': self._check_safety_requirements(),
            'Фотометрические требования': self._check_photometric_requirements(),
            'Требования энергоэффективности': self._check_energy_efficiency(),
            'Экологические требования': self._check_environmental_requirements()
        }

    def _check_safety_requirements(self):
        requirements = {
            'Класс защиты': self.fixture.protection in [ProtectionClass.IP44, ProtectionClass.IP54,
                                                        ProtectionClass.IP65],
            'Температурный диапазон': (-40 <= self.fixture.operating_temp[0] and self.fixture.operating_temp[1] <= 50),
            'Сопротивление изоляции': True
        }
        return requirements

    def _check_photometric_requirements(self):
        min_flux = {
            LampType.СВЕТОДИОДНАЯ: 80 * self.fixture.power,
            LampType.ГАЛОГЕННАЯ: 15 * self.fixture.power,
            LampType.ЛЮМИНЕСЦЕНТНАЯ: 50 * self.fixture.power,
            LampType.ЛАМПА_НАКАЛИВАНИЯ: 10 * self.fixture.power
        }
        requirements = {
            'Световой поток': self.fixture.luminous_flux >= min_flux.get(self.fixture.lamp_type, 0),
            'Цветовая температура': 2400 <= self.fixture.color_temp <= 6500,
            'Индекс цветопередачи': self.fixture.cri >= 80 if self.fixture.lamp_type == LampType.СВЕТОДИОДНАЯ else self.fixture.cri >= 70
        }
        return requirements

    def _check_energy_efficiency(self):
        efficacy = self.fixture.luminous_flux / self.fixture.power
        min_efficacy = {
            LampType.СВЕТОДИОДНАЯ: 90,
            LampType.ГАЛОГЕННАЯ: 15,
            LampType.ЛЮМИНЕСЦЕНТНАЯ: 60,
            LampType.ЛАМПА_НАКАЛИВАНИЯ: 10
        }
        requirements = {
            'Световая отдача': efficacy >= min_efficacy.get(self.fixture.lamp_type, 0),
            'Коэффициент мощности': True
        }
        return requirements

    def _check_environmental_requirements(self):
        requirements = {
            'Отсутствие ртути': self.fixture.lamp_type != LampType.ЛЮМИНЕСЦЕНТНАЯ,
            'Срок службы': self.fixture.lifetime >= 25000 if self.fixture.lamp_type == LampType.СВЕТОДИОДНАЯ else self.fixture.lifetime >= 1000
        }
        return requirements

    def get_results(self):
        return self.results


class ReportGenerator:
    def __init__(self):
        self._unique_reports = set()
        self._reports_data = []

    def add_report(self, fixture, results):
        report_id = fixture.get_unique_id()

        if report_id in self._unique_reports:
            return None

        self._unique_reports.add(report_id)
        report = self._generate_report(fixture, results)
        self._reports_data.append(report)
        return report

    def _generate_report(self, fixture, results):
        current_time = datetime.now().strftime("sss")
        report_lines = [
            "=" * 80,
            f"ОТЧЕТ О СООТВЕТСТВИИ ОСВЕТИТЕЛЬНОГО ПРИБОРА ГОСТ Р 54350-2015",
            f"Дата проверки: {current_time}",
            f"Модель прибора: {fixture.model}",
            "\nПАРАМЕТРЫ ПРИБОРА:",
            f"  Тип лампы: {fixture.lamp_type.name.replace('_', ' ')}",
            f"  Мощность: {fixture.power} Вт",
            f"  Световой поток: {fixture.luminous_flux} лм",
            f"  Цветовая температура: {fixture.color_temp} K",
            f"  Индекс цветопередачи: {fixture.cri}",
            f"  Класс защиты: {fixture.protection.name}",
            f"  Рабочий диапазон: {fixture.operating_temp[0]}...{fixture.operating_temp[1]} °C",
            f"  Срок службы: {fixture.lifetime} часов",
            "\nРЕЗУЛЬТАТЫ ПРОВЕРКИ:"
        ]

        for category, checks in results.items():
            report_lines.append(f"\n{category.upper()}:")
            for req, passed in checks.items():
                status = "Соответствует" if passed else "Не соответствует"
                report_lines.append(f"  - {req}: {status}")

        report_lines.append("=" * 80)
        return "\n".join(report_lines)

    def generate_combined_report(self):
        if not self._reports_data:
            return "Нет данных для формирования отчета"

        combined = [
            "ОБОБЩЕННЫЙ ОТЧЕТ ПО ПРОВЕРЕННЫМ ПРИБОРАМ",
            f"Дата формирования: {datetime.now().strftime('sss')}",
            f"Всего уникальных приборов: {len(self._reports_data)}",
            "=" * 80,
            ""
        ]

        for i, report in enumerate(self._reports_data, 1):
            combined.append(f"ОТЧЕТ #{i}:")
            combined.append(report)
            combined.append("")

        return "\n".join(combined)

    def save_to_file(self, content, filename=None):
        if not filename:
            filename = f"отчет_ГОСТ_{datetime.now().strftime('sss')}.txt"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            return filename
        except Exception as e:
            print(f"Ошибка при сохранении файла: {e}")
            return None


class Application:
    def __init__(self):
        self.report_generator = ReportGenerator()

    def run(self):
        print("ПРОГРАММА ПРОВЕРКИ СООТВЕТСТВИЯ ОСВЕТИТЕЛЬНЫХ ПРИБОРОВ")
        print("ГОСТ Р 54350-2015")
        print("=" * 60)

        while True:
            fixture = LightingFixture()
            fixture.input_parameters()

            checker = GOSTChecker(fixture)
            results = checker.get_results()

            report = self.report_generator.add_report(fixture, results)

            if report:
                print("\n" + "=" * 60)
                print("РЕЗУЛЬТАТЫ ПРОВЕРКИ:")
                print(report)
                print("=" * 60)

                self._handle_report_menu(report)
            else:
                print("\nПрибор с такими параметрами уже проверялся!")

            if input("\nПроверить другой прибор? (да/нет): ").lower() != 'да':
                break

        if self.report_generator._reports_data:
            combined = self.report_generator.generate_combined_report()
            print("\n" + "=" * 60)
            print(combined)

            if input("\nСохранить обобщенный отчет? (да/нет): ").lower() == 'да':
                filename = self.report_generator.save_to_file(combined)
                if filename:
                    print(f"Отчет сохранен в файл: {filename}")

        print("\nРабота программы завершена.")

    def _handle_report_menu(self, report):
        while True:
            print("\nМеню действий:")
            print("1. Сохранить текущий отчет")
            print("2. Продолжить проверку")
            choice = input("Выберите действие: ")

            if choice == '1':
                custom_name = input("Введите имя файла (или Enter для автоматического): ").strip()
                filename = self.report_generator.save_to_file(
                    report,
                    custom_name if custom_name else None
                )
                if filename:
                    print(f"Отчет сохранен в файл: {filename}")
            elif choice == '2':
                break
            else:
                print("Неверный ввод, попробуйте снова")


if __name__ == "__main__":
    app = Application()
    app.run()