from app.models import BaseModel

class Review(BaseModel):
    """
        Review model representing a review left by a user for a place.
    """

    def __init__(self, text, rating, user_id, place_id):
        """
            Initialize a Review instance
            Args:
                text (str): The review text
                rating (int): Rating from 1 to 5
                user_id (str): UUID of the user who wrote the review
                place_id (str): UUID of the place being reviewed
        """
        super().__init__() # Call __init__ of BaseModel
        self.text = text
        self.rating = rating
        self.user_id = user_id
        self.place_id = place_id
        # Validate rating on creation
        self.validate_rating()

    def validate_rating(self):
        """
            Validate rating value to ensure it's between 1 and 5

            Raises:
                ValueError: If rating is not between 1 and 5
        """
        if not isinstance(self.rating, int) or not (1 <= self.rating <= 5):
            raise ValueError("Rating must be an integer between 1 and 5")

    def to_dict(self):
        """Convert Review to dictionary format for API responses."""
        review_dict = super().to_dict() # Start with base attributes (id, created_at, updated_at)
        review_dict['text'] = self.text
        review_dict['rating'] = self.rating
        review_dict['user_id'] = self.user_id
        review_dict['place_id'] = self.place_id
        return review_dict

    @staticmethod
    def list_by_place(place_id):
        """
            List all reviews for a specific place

            Args:
                place_id (str): UUID of the place to list reviews for

            Returns:
                list: List of Review objects for the specified place
        """
        # Only a placeholder. In Part3, we will implement actual data retrieval.
        pass
