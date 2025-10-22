        return placed_count

    def _enhanced_gap_filling(self, all_needs: List[Dict]) -> int:
        """
        Enhanced gap filling strategy to improve coverage
        """
        gap_filled_count = 0
        
        # Try to fill gaps for each need that wasn't fully scheduled
        for need in all_needs:
            scheduled = need.get("scheduled", 0)
            weekly_hours = need.get("weekly_hours", 0)
            
            if scheduled < weekly_hours:
                remaining = weekly_hours - scheduled
                self.logger.info(f"     Gap filling for {need.get('class_name', 'Unknown')} - "
                               f"{need.get('lesson_name', 'Unknown')}: {remaining} hours")
                
                # Try aggressive placement for remaining hours
                filled = self._aggressive_placement_for_need(need, remaining)
                gap_filled_count += filled
                
        return gap_filled_count

    def _aggressive_placement_for_need(self, need: Dict, remaining_hours: int) -> int:
        """
        Aggressively place remaining hours for a specific need
        """
        filled_count = 0
        class_id = need["class_id"]
        teacher_id = need["teacher_id"]
        lesson_id = need["lesson_id"]
        
        # Try placement with relaxed constraints
        for day in range(5):  # 5 days
            if filled_count >= remaining_hours:
                break
                
            for time_slot in range(8):  # Try up to 8 time slots
                if filled_count >= remaining_hours:
                    break
                    
                # Try to place with relaxed constraints
                can_place = self._can_place_relaxed(
                    class_id, teacher_id, day, time_slot
                )
                
                if can_place:
                    # Place the lesson
                    classroom_id = 1  # Default classroom
                    self._add_entry(class_id, teacher_id, lesson_id, classroom_id, day, time_slot)
                    filled_count += 1
                    need["scheduled"] = need.get("scheduled", 0) + 1
                    
                    self.logger.info(f"       ✓ Aggressively placed: Day {day+1}, Slot {time_slot+1}")
        
        return filled_count