from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=3)

class TaskManager:
    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def run_task(self, task):
        executor.submit(task)

    def run_all(self):
        for task in self.tasks:
            self.run_task(task)
        self.tasks = []

    def clear_tasks(self):
        self.tasks = []
        executor.shutdown(wait=False)

task_manager = TaskManager()