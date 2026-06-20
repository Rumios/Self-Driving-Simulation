class RuleManager():
    def __init__(self, vehicle, obstacles):
        self.vehicle = vehicle
        self.obstacles = obstacles
        self.is_collided = False
        
    def check_collision(self):
        # 폴리곤의 vertices가 내부에 있는지 검사
        vehicle_vertices = self.vehicle.get_vertices()
        
        for obj in self.obstacles:
            for vx, vy in vehicle_vertices:
                # 충돌 시
                if obj.rect.collidepoint(vx, vy):
                    return True
        
        return False

    def update(self):
        # 지금은 임시로 충돌 여부만 표시 (디버깅용)
        current_collision = self.check_collision()
        
        if current_collision and not self.is_collided:
            self.is_collided = True
            
        return current_collision