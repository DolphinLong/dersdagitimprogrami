from database.db_manager import DatabaseManager

def check_class_distribution():
    db = DatabaseManager()
    classes = db.get_all_classes()
    
    print(f"Total classes: {len(classes)}")
    
    grade_counts = {}
    for c in classes:
        grade_counts[c.grade] = grade_counts.get(c.grade, 0) + 1
    
    for grade in sorted(grade_counts.keys()):
        print(f'Grade {grade}: {grade_counts[grade]} classes')
    
    print("\nAll classes:")
    for c in classes:
        print(f"  {c.name} (Grade {c.grade})")
    
    db.close()

if __name__ == "__main__":
    check_class_distribution()