"""
Shopping cart utilities for book holds.
Uses Django session to store cart items before confirmation.
"""


class Cart:
    """
    Shopping cart for book holds stored in session.
    """
    
    def __init__(self, request):
        """
        Initialize cart from session.
        """
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            # Initialize empty cart
            cart = self.session['cart'] = {}
        self.cart = cart
    
    def add(self, book_id):
        """
        Add a book to the cart.
        
        Args:
            book_id: ID of the book to add
        """
        book_id_str = str(book_id)
        if book_id_str not in self.cart:
            self.cart[book_id_str] = {
                'book_id': book_id,
            }
            self.save()
            return True
        return False  # Book already in cart
    
    def remove(self, book_id):
        """
        Remove a book from the cart.
        
        Args:
            book_id: ID of the book to remove
        """
        book_id_str = str(book_id)
        if book_id_str in self.cart:
            del self.cart[book_id_str]
            self.save()
            return True
        return False
    
    def clear(self):
        """
        Clear all items from cart.
        """
        self.session['cart'] = {}
        self.cart = {}
        self.save()
    
    def get_book_ids(self):
        """
        Get list of book IDs in cart.
        
        Returns:
            List of book IDs (as integers)
        """
        return [int(item['book_id']) for item in self.cart.values()]
    
    def count(self):
        """
        Get number of items in cart.
        
        Returns:
            Integer count of cart items
        """
        return len(self.cart)
    
    def __len__(self):
        """
        Return the number of items in cart.
        """
        return self.count()
    
    def __contains__(self, book_id):
        """
        Check if a book is in the cart.
        """
        return str(book_id) in self.cart
    
    def save(self):
        """
        Mark session as modified to ensure it's saved.
        """
        self.session.modified = True
