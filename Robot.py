from queue import PriorityQueue

class Robot:
    def __init__(self, start_position):
        self.position = start_position
        self.path = []

    def find_path(self, start, goal, rows, cols, obstacles):
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        frontier = PriorityQueue()
        frontier.put((0, start))
        came_from = {}
        cost_so_far = {}

        came_from[start] = None
        cost_so_far[start] = 0

        while not frontier.empty():
            _, current = frontier.get()

            if current == goal:
                break

            for dx, dy in [(-1,  0), (1,  0), (0, -1), (0, 1),
                           (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                next_node = (current[0] + dx, current[1] + dy)
                if (0 <= next_node[0] < rows and 0 <= next_node[1] < cols and
                    next_node not in obstacles):
                    new_cost = cost_so_far[current] + (1.414 if dx != 0 and dy != 0 else 1)
                    if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                        cost_so_far[next_node] = new_cost
                        priority = new_cost + heuristic(goal, next_node)
                        frontier.put((priority, next_node))
                        came_from[next_node] = current

        current = goal
        path = []
        while current != start:
            path.append(current)
            current = came_from.get(current)
            if current is None:
                return []
        path.append(start)
        path.reverse()
        return path
