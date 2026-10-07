import argparse
import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

SUBJECTS = ["math", "science", "english", "history", "art"]


@dataclass
class StudentRecord:
    name: str
    scores: Dict[str, int] = field(default_factory=dict)

    def average_score(self) -> float:
        return round(sum(self.scores.values()) / len(self.scores), 2)

    def grade(self) -> str:
        average = self.average_score()
        if average >= 90:
            return "A"
        if average >= 80:
            return "B"
        if average >= 70:
            return "C"
        if average >= 60:
            return "D"
        return "F"


def load_students(csv_path: str) -> List[StudentRecord]:
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    students: List[StudentRecord] = []
    with path.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            name = (row.get("name") or "").strip()
            if not name:
                continue

            scores = {}
            for subject in SUBJECTS:
                value = (row.get(subject) or "").strip()
                try:
                    scores[subject] = int(value)
                except (TypeError, ValueError):
                    scores[subject] = 0

            students.append(StudentRecord(name=name, scores=scores))

    if not students:
        raise ValueError(f"No valid student data was found in: {csv_path}")

    return students


def assign_grade(score: float) -> str:
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


class StudentPerformanceAnalyzer:
    def __init__(self, students: List[StudentRecord]):
        self.students = students

    def class_statistics(self) -> Dict[str, float]:
        stats: Dict[str, float] = {}
        for subject in SUBJECTS:
            values = [student.scores.get(subject, 0) for student in self.students]
            if values:
                stats[subject] = round(sum(values) / len(values), 2)
        return stats

    def strongest_subjects(self, limit: int = 3) -> List[tuple]:
        data = []
        for subject in SUBJECTS:
            values = [student.scores.get(subject, 0) for student in self.students]
            if values:
                data.append((subject, round(sum(values) / len(values), 2)))
        data.sort(key=lambda item: item[1], reverse=True)
        return data[:limit]

    def weakest_subjects(self, limit: int = 3) -> List[tuple]:
        data = []
        for subject in SUBJECTS:
            values = [student.scores.get(subject, 0) for student in self.students]
            if values:
                data.append((subject, round(sum(values) / len(values), 2)))
        data.sort(key=lambda item: item[1])
        return data[:limit]

    def top_students(self, limit: int = 5) -> List[dict]:
        ranked = []
        for student in self.students:
            ranked.append({
                "name": student.name,
                "average": student.average_score(),
                "grade": student.grade(),
            })
        ranked.sort(key=lambda item: item["average"], reverse=True)
        return ranked[:limit]

    def find_student(self, name: str) -> Optional[StudentRecord]:
        query = name.strip().lower()
        for student in self.students:
            if student.name.lower() == query:
                return student
        return None

    def generate_report(self) -> str:
        class_stats = self.class_statistics()
        strongest = self.strongest_subjects()
        weakest = self.weakest_subjects()
        top_students = self.top_students(5)

        lines = [
            "Student Performance Analysis Report",
            "=" * 40,
            "Class Statistics:",
        ]

        for subject, value in class_stats.items():
            lines.append(f"- {subject.title()}: {value}% (Grade {assign_grade(value)})")

        lines.extend(["", "Strongest Subjects:"])
        for subject, value in strongest:
            lines.append(f"- {subject.title()}: {value}%")

        lines.extend(["", "Weakest Subjects:"])
        for subject, value in weakest:
            lines.append(f"- {subject.title()}: {value}%")

        lines.extend(["", "Top Students:"])
        for index, student in enumerate(top_students, start=1):
            lines.append(f"{index}. {student['name']} - Average: {student['average']}% - Grade: {student['grade']}")

        return "\n".join(lines)

    def export_report(self, output_path: str) -> str:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        report = self.generate_report()
        path.write_text(report, encoding="utf-8")
        return str(path)


def main():
    parser = argparse.ArgumentParser(description="Analyze student performance from CSV data.")
    parser.add_argument("--csv", required=True, help="Path to the CSV file.")
    parser.add_argument("--search", help="Search for a student by name.")
    parser.add_argument("--top", type=int, default=5, help="Number of top-performing students to show.")
    parser.add_argument("--export", help="Export a report to a text file.")
    args = parser.parse_args()

    try:
        students = load_students(args.csv)
        analyzer = StudentPerformanceAnalyzer(students)

        print("\nClass Statistics:")
        for subject, average in analyzer.class_statistics().items():
            print(f"  - {subject.title()}: {average}% ({assign_grade(average)})")

        print("\nStrongest Subjects:")
        for subject, average in analyzer.strongest_subjects():
            print(f"  - {subject.title()}: {average}%")

        print("\nWeakest Subjects:")
        for subject, average in analyzer.weakest_subjects():
            print(f"  - {subject.title()}: {average}%")

        print("\nTop Students:")
        for student in analyzer.top_students(args.top):
            print(f"  - {student['name']}: {student['average']}% ({student['grade']})")

        if args.search:
            student = analyzer.find_student(args.search)
            if student:
                print(f"\nStudent Found: {student.name}")
                print(f"Average: {student.average_score()}%")
                print(f"Grade: {student.grade()}")
                for subject, score in student.scores.items():
                    print(f"  - {subject.title()}: {score}")
            else:
                print(f"\nNo student named '{args.search}' was found.")

        if args.export:
            output_file = analyzer.export_report(args.export)
            print(f"\nReport exported to: {output_file}")

    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
