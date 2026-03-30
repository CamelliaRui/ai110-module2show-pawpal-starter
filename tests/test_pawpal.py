from pawpal_system import Task, Pet


def test_mark_complete_changes_status():
    """Verify that calling mark_complete() actually changes the task's status."""
    task = Task("Walk", 20, "high")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_mark_incomplete_changes_status():
    """Verify that mark_incomplete() reverts a completed task."""
    task = Task("Walk", 20, "high")
    task.mark_complete()
    assert task.completed is True
    task.mark_incomplete()
    assert task.completed is False


def test_adding_task_increases_pet_task_count():
    """Verify that adding a task to a Pet increases that pet's task count."""
    pet = Pet("Mochi", "dog")
    assert len(pet.tasks) == 0
    pet.add_task(Task("Walk", 20, "high"))
    assert len(pet.tasks) == 1
    pet.add_task(Task("Feed", 10, "medium"))
    assert len(pet.tasks) == 2
