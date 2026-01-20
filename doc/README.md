# Basic Design

This web-application will basically a roaster shuffle program for tennis match.
But, it can be used any events.

## Simple description:

Initially, the event organizer will create an event in the website.
(Website will provide "create event" button).
(Of course, the event can be deleted by the organizer.)
(For convenience, the event can be copied to a new event, which carries over the participants.)

Then, participants will register on their own in the event.
(Website will provide "register" button).
(This will form a "Pool" of participants in the event. )
(Of course, the participant can be deleted by the organizer.)

After all participants registered, the organizer will decide how many teams will be formed.
(Website will provide "set number of teams" button).

For simplicity, this program will assume double matches, so there will be 2 players in each team.
Probably total number of participants will be more than the total number players for a tournament.
So, we will form a "Roaster" from the Pool.
(Roaster is a subset of Pool.)
(Pool and Roaster are showing on the same page.)


Initially, Pool has entire participants, and each participant is a Javascript button.

When the organizer clicks a participant button, it will be moved to Roaster.
(The button will be removed from Pool and added to Roaster as a button.)

Same will happen on the Roaster side. If the name on the roaster button is clicked, it will be moved back to Pool.

Note that, we are starting with a simplified case.  There is no distinction between "Participants" and "Organizers" in multi-user environment.  So, change must happen in the server.
Which means, each click of Roaster or Pool button will update the server.  So, hopefully, it is running like a AJAX application, (change happens in server every time, but page refresh is not entirely done.  Only update Roaster/Pool at the moment of a button click.)

