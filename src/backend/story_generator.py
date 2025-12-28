"""
Infinite Story Web - Procedural Story Generator

This module provides the story generation engine that creates
procedurally evolving narratives based on user interactions.
"""

import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class Mood(Enum):
    """Story mood types that influence narrative generation."""
    MYSTERIOUS = "mysterious"
    ADVENTUROUS = "adventurous"
    DARK = "dark"
    WHIMSICAL = "whimsical"
    ROMANTIC = "romantic"
    SUSPENSEFUL = "suspenseful"
    PHILOSOPHICAL = "philosophical"


class Genre(Enum):
    """Story genre types."""
    FANTASY = "fantasy"
    SCIFI = "scifi"
    HORROR = "horror"
    ROMANCE = "romance"
    ADVENTURE = "adventure"
    MYSTERY = "mystery"


@dataclass
class StoryContext:
    """Context for story generation."""
    current_mood: Mood
    genre: Genre
    characters: List[str]
    locations: List[str]
    themes: List[str]
    tension_level: float  # 0.0 to 1.0
    story_length: int
    recent_events: List[str]


class StoryGenerator:
    """Procedural story generation engine."""

    # Story building blocks
    OPENINGS = {
        Genre.FANTASY: [
            "In a realm where magic flows like rivers,",
            "Beyond the mountains of the Eternal Dawn,",
            "The ancient prophecy spoke of this moment:",
            "In the kingdom of forgotten dreams,",
            "Where dragons once soared and wizards walked,",
        ],
        Genre.SCIFI: [
            "The starship hummed with quiet energy as",
            "Across the void of space, a signal emerged:",
            "In the year 3047, humanity discovered",
            "The android's circuits flickered as",
            "On the colony ship Eternal Hope,",
        ],
        Genre.HORROR: [
            "The shadows seemed to breathe as",
            "Something ancient stirred beneath the surface:",
            "The night grew darker than it should have,",
            "Fear crept in like cold fingers,",
            "What lurked in the darkness was",
        ],
        Genre.ROMANCE: [
            "Their eyes met across the crowded room,",
            "Love, they say, arrives unexpectedly:",
            "The heart knows what the mind denies,",
            "In that moment, everything changed between them:",
            "Some connections transcend explanation,",
        ],
        Genre.ADVENTURE: [
            "The journey ahead would test their limits,",
            "Adventure called from beyond the horizon,",
            "With courage in their heart, they stepped forward:",
            "The map revealed a path unknown,",
            "Every great story begins with a single step,",
        ],
        Genre.MYSTERY: [
            "The clues didn't add up, but then",
            "Something was terribly wrong here,",
            "The detective noticed what others missed:",
            "Secrets have a way of revealing themselves,",
            "The truth was hidden in plain sight,",
        ],
    }

    CHARACTERS = [
        "the wanderer", "an ancient guardian", "a lost child",
        "the mysterious stranger", "a forgotten hero", "the wise elder",
        "a curious inventor", "the silent observer", "a fierce warrior",
        "the healer", "a cunning thief", "the dreamer",
        "a brave captain", "the oracle", "a rebellious spirit",
    ]

    LOCATIONS = [
        "the crystalline caves", "an abandoned city", "the floating islands",
        "the endless forest", "a hidden sanctuary", "the storm-torn sea",
        "the ancient library", "a forgotten temple", "the mirror dimension",
        "the twilight valley", "a mechanical heart", "the dream realm",
    ]

    ACTIONS = {
        Mood.MYSTERIOUS: [
            "discovered a hidden truth that changed everything",
            "encountered something that defied explanation",
            "followed whispers that led to ancient secrets",
            "uncovered a mystery spanning centuries",
            "realized nothing was as it seemed",
        ],
        Mood.ADVENTUROUS: [
            "embarked on a perilous journey",
            "faced dangers that would break lesser souls",
            "discovered uncharted territories",
            "conquered impossible challenges",
            "found strength they never knew existed",
        ],
        Mood.DARK: [
            "confronted the darkness within",
            "witnessed horrors that haunted their dreams",
            "made a sacrifice that cost everything",
            "faced the abyss and it stared back",
            "lost something precious to the shadows",
        ],
        Mood.WHIMSICAL: [
            "stumbled upon something wonderfully absurd",
            "found magic in the most unexpected place",
            "danced with creatures of pure imagination",
            "discovered that nonsense held the answers",
            "laughed in the face of impossibility",
        ],
        Mood.ROMANTIC: [
            "felt their heart skip in unexpected ways",
            "discovered love blooming in darkness",
            "risked everything for a moment together",
            "found connection transcending all barriers",
            "realized love was worth any sacrifice",
        ],
        Mood.SUSPENSEFUL: [
            "felt time slowing as danger approached",
            "held their breath as fate hung in balance",
            "watched helplessly as events unfolded",
            "faced a choice that would change everything",
            "sensed something terrible was about to happen",
        ],
        Mood.PHILOSOPHICAL: [
            "questioned the nature of their reality",
            "pondered the meaning of their existence",
            "discovered truth was more complex than imagined",
            "realized wisdom came from unexpected sources",
            "understood that some questions have no answers",
        ],
    }

    TRANSITIONS = [
        "Meanwhile,", "As time passed,", "Without warning,",
        "In the silence that followed,", "Against all odds,",
        "When hope seemed lost,", "At the edge of reason,",
        "Through the mist of uncertainty,", "In that pivotal moment,",
        "As fate would have it,", "Beyond the veil of reality,",
    ]

    TENSION_MODIFIERS = {
        'low': [
            "A sense of calm settled over",
            "Peace, however brief, brought clarity to",
            "In the quiet moments,",
        ],
        'medium': [
            "Uncertainty hung in the air as",
            "The stakes grew higher when",
            "A turning point approached as",
        ],
        'high': [
            "Heart pounding, they realized",
            "There was no turning back now as",
            "Everything converged in this moment:",
        ],
    }

    def __init__(self, seed: Optional[int] = None):
        """Initialize the story generator.
        
        Args:
            seed: Optional random seed for reproducibility
        """
        if seed is not None:
            random.seed(seed)
        
        self.context = self._create_initial_context()

    def _create_initial_context(self) -> StoryContext:
        """Create initial story context."""
        return StoryContext(
            current_mood=random.choice(list(Mood)),
            genre=random.choice(list(Genre)),
            characters=[random.choice(self.CHARACTERS)],
            locations=[random.choice(self.LOCATIONS)],
            themes=[],
            tension_level=0.3,
            story_length=0,
            recent_events=[]
        )

    def generate_opening(self) -> str:
        """Generate an opening for a new story."""
        opening = random.choice(self.OPENINGS[self.context.genre])
        character = random.choice(self.CHARACTERS)
        location = random.choice(self.LOCATIONS)
        
        self.context.characters.append(character)
        self.context.locations.append(location)
        
        segment = f"{opening} {character} arrived at {location}."
        self.context.story_length += len(segment.split())
        self.context.recent_events.append("story_opening")
        
        return segment

    def generate_segment(self, interaction_data: Optional[Dict[str, Any]] = None) -> str:
        """Generate a new story segment based on current context and interactions.
        
        Args:
            interaction_data: Optional data about user interactions
            
        Returns:
            A new story segment
        """
        # Apply interaction influence
        if interaction_data:
            self._apply_interaction_influence(interaction_data)
        
        # Build the segment
        parts = []
        
        # Add transition
        if random.random() > 0.3:
            parts.append(random.choice(self.TRANSITIONS))
        
        # Add tension modifier based on current tension level
        if random.random() > 0.5:
            if self.context.tension_level < 0.33:
                parts.append(random.choice(self.TENSION_MODIFIERS['low']))
            elif self.context.tension_level < 0.66:
                parts.append(random.choice(self.TENSION_MODIFIERS['medium']))
            else:
                parts.append(random.choice(self.TENSION_MODIFIERS['high']))
        
        # Pick a character and action
        character = random.choice(self.context.characters) if self.context.characters else random.choice(self.CHARACTERS)
        action = random.choice(self.ACTIONS[self.context.current_mood])
        
        # Sometimes add location context
        if random.random() > 0.6:
            location = random.choice(self.context.locations) if self.context.locations else random.choice(self.LOCATIONS)
            parts.append(f"{character} {action} in {location}.")
        else:
            parts.append(f"{character} {action}.")
        
        # Maybe introduce new elements
        if random.random() > 0.7:
            new_char = random.choice(self.CHARACTERS)
            if new_char not in self.context.characters:
                self.context.characters.append(new_char)
                parts.append(f"It was then that {new_char} appeared.")
        
        segment = ' '.join(parts)
        
        # Update context
        self.context.story_length += len(segment.split())
        self._evolve_context()
        
        return segment

    def _apply_interaction_influence(self, data: Dict[str, Any]) -> None:
        """Apply user interaction influence to story generation.
        
        Args:
            data: Interaction data including type and details
        """
        interaction_type = data.get('type', '')
        
        if interaction_type == 'scroll':
            # Scrolling affects pacing - more scroll = faster story progression
            scroll_amount = data.get('amount', 0)
            if scroll_amount > 100:
                self.context.tension_level = min(1.0, self.context.tension_level + 0.1)
            
        elif interaction_type == 'click':
            # Clicking introduces new elements
            if random.random() > 0.5:
                new_location = random.choice(self.LOCATIONS)
                if new_location not in self.context.locations:
                    self.context.locations.append(new_location)
            
        elif interaction_type == 'keypress':
            # Keypresses affect mood
            key = data.get('key', '')
            mood_map = {
                'm': Mood.MYSTERIOUS,
                'a': Mood.ADVENTUROUS,
                'd': Mood.DARK,
                'w': Mood.WHIMSICAL,
                'r': Mood.ROMANTIC,
                's': Mood.SUSPENSEFUL,
                'p': Mood.PHILOSOPHICAL,
            }
            if key.lower() in mood_map:
                self.context.current_mood = mood_map[key.lower()]

    def _evolve_context(self) -> None:
        """Naturally evolve the story context over time."""
        # Mood might shift randomly
        if random.random() > 0.85:
            self.context.current_mood = random.choice(list(Mood))
        
        # Tension naturally oscillates
        tension_change = random.uniform(-0.1, 0.15)
        self.context.tension_level = max(0.0, min(1.0, self.context.tension_level + tension_change))
        
        # Occasionally shift genre slightly (rare)
        if random.random() > 0.95:
            self.context.genre = random.choice(list(Genre))

    def merge_storylines(self, other_segments: List[str]) -> str:
        """Merge segments from another storyline into the current one.
        
        Args:
            other_segments: Story segments from another user's storyline
            
        Returns:
            A merged story segment
        """
        if not other_segments:
            return self.generate_segment()
        
        # Pick a segment to merge from
        merge_segment = random.choice(other_segments)
        
        # Create a merge transition
        merge_transitions = [
            "As realities collided,",
            "In a twist of fate,",
            "The timelines merged when",
            "Suddenly, another story intersected:",
            "From a parallel path came",
        ]
        
        transition = random.choice(merge_transitions)
        
        # Extract some essence from the other segment
        words = merge_segment.split()
        if len(words) > 5:
            essence = ' '.join(words[:min(10, len(words))])
        else:
            essence = merge_segment
        
        merged = f"{transition} {essence}... And so the stories became one."
        
        self.context.recent_events.append("storyline_merge")
        
        return merged

    def get_context_summary(self) -> Dict[str, Any]:
        """Get a summary of the current story context."""
        return {
            'mood': self.context.current_mood.value,
            'genre': self.context.genre.value,
            'characters': list(set(self.context.characters)),
            'locations': list(set(self.context.locations)),
            'tension_level': self.context.tension_level,
            'story_length': self.context.story_length,
        }

    def set_mood(self, mood: str) -> bool:
        """Set the story mood.
        
        Args:
            mood: Mood name to set
            
        Returns:
            True if mood was set successfully
        """
        try:
            self.context.current_mood = Mood(mood)
            return True
        except ValueError:
            return False

    def set_genre(self, genre: str) -> bool:
        """Set the story genre.
        
        Args:
            genre: Genre name to set
            
        Returns:
            True if genre was set successfully
        """
        try:
            self.context.genre = Genre(genre)
            return True
        except ValueError:
            return False

    def reset(self) -> None:
        """Reset the story generator to initial state."""
        self.context = self._create_initial_context()
