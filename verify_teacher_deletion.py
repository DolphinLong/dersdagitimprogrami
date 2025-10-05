from database import db_manager

def verify_teacher_deletion():
    print("Verifying teacher deletion fix...")
    
    # Try to find the deleted teacher (Ali with ID 1)
    teacher = db_manager.get_teacher_by_id(1)
    if teacher:
        print(f"ERROR: Teacher still exists: {teacher.name}")
        return False
    else:
        print("✓ Teacher successfully deleted")
    
    # Check if related records were also deleted
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    # Check schedule entries
    cursor.execute("SELECT COUNT(*) FROM schedule_entries WHERE teacher_id = 1")
    count = cursor.fetchone()[0]
    if count == 0:
        print("✓ Schedule entries successfully deleted")
    else:
        print(f"ERROR: {count} schedule entries still exist")
        return False
    
    # Check teacher availability
    cursor.execute("SELECT COUNT(*) FROM teacher_availability WHERE teacher_id = 1")
    count = cursor.fetchone()[0]
    if count == 0:
        print("✓ Teacher availability records successfully deleted")
    else:
        print(f"ERROR: {count} availability records still exist")
        return False
    
    # Check guidance counselor assignments
    cursor.execute("SELECT COUNT(*) FROM guidance_counselor_assignments WHERE teacher_id = 1")
    count = cursor.fetchone()[0]
    if count == 0:
        print("✓ Guidance counselor assignments successfully deleted")
    else:
        print(f"ERROR: {count} guidance assignments still exist")
        return False
    
    print("\nAll verifications passed! Teacher deletion is now working correctly.")
    return True

if __name__ == "__main__":
    verify_teacher_deletion()
    db_manager.close()