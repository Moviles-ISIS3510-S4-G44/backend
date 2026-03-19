Este es el modelo mínimo actual del backend para un university marketplace MVP.

Entidades actuales:
- User
- Listing
- Category

Decisiones:
1. Product no existe como entidad separada.
2. Location no es entidad; es un atributo simple dentro de Listing.
3. Listing es la entidad principal del marketplace.
4. Listing absorbe título, descripción, categoría, precio, condición, imágenes y ubicación.
5. La primera imagen de Listing.images será la portada visual del item en el feed.
6. User crea Listings.
7. Listing pertenece a una Category.
8. User.rating debe tratarse como derivado o secundario.
9. Por ahora no incluir Transaction, Conversation, Message ni Review en la API base si no son necesarias para las features actuales.
10. Este modelo busca cubrir login/signup, home marketplace, product detail y create listing con el mínimo dominio posible.