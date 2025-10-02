from sqlalchemy.orm import Session
from . import models

def create_test_data(db: Session):
    """Создание тестовых данных для разработки"""
    
    # Проверяем, есть ли уже проекты
    existing_projects = db.query(models.Project).count()
    if existing_projects > 0:
        print("✅ Тестовые данные уже существуют")
        return
    
    # Создаем тестовые проекты
    project1 = models.Project(
        name="ЖК 'Северный'",
        description="Многоэтажный жилой комплекс",
        address="ул. Строителей, 15",
        status="активный",
        created_by=1
    )
    
    project2 = models.Project(
        name="Бизнес-центр 'Плаза'", 
        description="Офисный центр класса А",
        address="пр. Мира, 28",
        status="активный",
        created_by=1
    )
    
    db.add(project1)
    db.add(project2)
    db.commit()
    db.refresh(project1)
    db.refresh(project2)
    
    # Создаем тестовые дефекты с правильными Enum значениями
    defect1 = models.Defect(
        project_id=project1.id,
        title="Трещина в несущей стене",
        description="Обнаружена вертикальная трещина в несущей стене на 3 этаже",
        priority=models.PriorityLevel.HIGH,  # Используем Enum, а не строку
        status=models.DefectStatus.NEW,      # Используем Enum, а не строку
        reported_by=1
    )
    
    defect2 = models.Defect(
        project_id=project1.id,
        title="Протечка кровли",
        description="Протечка в районе вентиляционных шахт",
        priority=models.PriorityLevel.MEDIUM,  # Используем Enum
        status=models.DefectStatus.IN_PROGRESS, # Используем Enum
        reported_by=1
    )
    
    db.add(defect1)
    db.add(defect2)
    db.commit()
    
    print("✅ Тестовые данные созданы")