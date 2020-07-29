# Twello

As part of the CS50X course I created a webapp that combines functionality similar to Twitter & Trello. The idea to create a Trello clone came from the sudden work-from-home transition within my team. I was looking for a replacement of our physical kanban boards to track tasks, but our company doesn't allow external services such as Trello. I decided to build my own version, which I will try to host internally on company infrastructure, so that it is somewhat compliant. 

I wanted to continue on the learnings from the web track, and build a Flask web application. I struggled a bit to get started as I needed a full blown web application with proper user management and security etc, and I wanted to build it from scratch to understand all the concepts. I found Miguel Grinberg's excellent "Flask Mega Tutorial", which guides you through all aspects of building a 'Microblog', using Flask & SQLAlchemy.

After completing the tutorial I extended the application with a "Boards" section that allows a user to create boards, in which a user can create lists and inside those lists you can add cards. Lists can be dragged in order, and cards can be sorted across lists using the SortableJS library. These actions are written to the database using ajax requests.

The UI is still a bit rough, and the application currently lacks the ability to participate on other boards.

