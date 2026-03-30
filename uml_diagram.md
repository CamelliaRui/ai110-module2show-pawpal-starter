# PawPal+ Final UML Class Diagram

```mermaid
classDiagram
    class Task {
        +str title
        +int duration_minutes
        +str priority
        +str category
        +str frequency
        +bool completed
        +time scheduled_time
        +date due_date
        +mark_complete() Task
        +mark_incomplete()
        -_create_next_occurrence(days) Task
    }

    class Pet {
        +str name
        +str species
        +List~Task~ tasks
        +add_task(task)
        +remove_task(title)
        +get_pending_tasks() List~Task~
        +complete_task(title) Task
    }

    class Owner {
        +str name
        +List~Pet~ pets
        +time start_time
        +time end_time
        +add_pet(pet)
        +get_all_tasks() List~Task~
        +get_all_pending_tasks() List~Task~
        +available_minutes() int
    }

    class ScheduledTask {
        +Task task
        +str pet_name
        +time start_time
        +time end_time
        +str reason
    }

    class Schedule {
        +List~ScheduledTask~ scheduled_tasks
        +bool over_capacity
        +int total_minutes
        +int available_minutes
        +List~str~ conflicts
        +display() str
    }

    class Scheduler {
        +Owner owner
        +generate_schedule() Schedule
        +filter_by_pet(name) List
        +filter_by_status(completed) List
        +sort_by_time(tasks) List
        -_gather_tasks() List
        -_sort_by_priority_and_time(tasks) List
        -_assign_time_slots(tasks) List~ScheduledTask~
        -_detect_conflicts(scheduled) List~str~
    }

    Owner "1" --> "*" Pet : manages
    Pet "1" --> "*" Task : has
    Scheduler --> Owner : reads from
    Scheduler --> Schedule : produces
    Schedule --> ScheduledTask : contains many
    ScheduledTask --> Task : wraps
    Task --> Task : creates next (recurring)
```
