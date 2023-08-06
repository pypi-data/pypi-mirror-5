models.py
*******************



Every pTree app needs 4 core database models 
(for background, read about Django models `here <https://docs.djangoproject.com/en/dev/topics/db/models/>`_):

- Participant
- Match
- Treatment
- Experiment

They are related to each other as follows:

A ``Participant`` is part of a ``Match``, which is part of a ``Treatment``, which is part of an ``Experiment``.

Furthermore, there are usually multiple ``Participant`` objects in a ``Match``, 
multiple ``Match`` objects in a ``Treatment``, 
and multiple ``Treatment`` objects in an ``Experiment``, meaning that your objects would look something like this:

.. image:: model-hierarchy.png

Participant
~~~~~~~~~~~

A ``Participant`` is a person who participates in a ``Match``.
For example, a Dictator Game match has 2 ``Participant`` objects.

A match can contain only 1 ``Participant`` if there is no interaction between ``Participant`` objects.
For example, a game that is simply a survey.

A ``Participant`` object should store any attributes that need to be stored for each Participant in the match.



Implementation
______________

``Participant`` classes should inherit from ``ptree.models.participants.BaseParticipant``. Here is the class structure:

.. py:class:: Participant

    .. py:method:: bonus(self)
    
        *You must implement this method.*

        The bonus the ``Participant`` gets paid, in addition to their base pay.
    
    .. py:attribute:: code = ptree.models.common.RandomCharField(length = 8)
    
        the participant's unique ID (and redemption code) that gets passed in the URL.
        This is generated automatically.
        
    .. py:attribute:: has_visited = models.BooleanField()
    
        whether the participant has visited our site at all.
    
    .. py:attribute:: index = models.PositiveIntegerField(null = True)
    
        the ordinal position in which a participant joined a game. Starts at 0.
    
    .. py:attribute:: is_finished = models.BooleanField()
    
        whether the participant is finished playing (i.e. has seen the redemption code page).

        
           
Match
~~~~~

A Match is a particular instance of a game being played,
and holds the results of that instance, i.e. what the score was, who got paid what.

So, "Match" is used in the sense of "boxing match",
in the sense that it is an event that occurs where the game is played.

Example of a Match: "dictator game between participants Alice & Bob, where Alice gave $0.50"

Implementation
______________

``Match`` classes should inherit from ``ptree.models.participants.BaseMatch``. Here is the class structure:

.. py:class:: Match

    .. py:method:: is_ready_for_next_participant(self)
    
        *You must implement this method yourself.*
        
        Whether the game is ready for another participant to be added.
        
        If it's a non-sequential game (you do not have to wait for one participant to finish before the next one joins),
        you can use this to assign participants until the game is full::
        
            return not self.is_full()

    .. py:method:: is_full(self)
    
        Whether the match is full (i.e. no more Participants can be assigned).
    
    .. py:method:: is_finished(self)
    
        Whether the match is completed.
        
    .. py:method:: participants(self)
    
        Returns the ``Participant`` objects in this match. 
        Syntactic sugar for ``self.participant_set.all()``
        
        


Treatment
~~~~~~~~~

A Treatment is the definition of what everyone in the treatment group has to do.

Example of a treatment:
'dictator game with stakes of $1, where participants have to chat with each other first'

A treatment is defined before the experiment starts.
Results of a game are not stored in ther Treatment object, they are stored in Match or Participant objects.

Implementation
______________

``Treatment`` classes should inherit from ``ptree.models.participants.BaseTreatment``. Here is the class structure:

.. py:class:: Treatment

    .. py:method:: sequence(self):
    
        *You must implement this method.*

        Very important. Returns a list of all the View classes that the participant gets routed through sequentially.
        (Not all pages have to be displayed for all participants; see the ``is_displayed()`` method)
        
        Example::
            
            import donation.views as views
            import ptree.views.concrete
            return [views.Start,
                    ptree.views.concrete.AssignParticipantAndMatch,
                    views.IntroPage,
                    views.EnterOfferEncrypted, 
                    views.ExplainRandomizationDetails, 
                    views.EnterDecryptionKey,
                    views.NotifyOfInvalidEncryptedDonation,
                    views.EnterOfferUnencrypted,
                    views.NotifyOfShred,
                    views.Survey,
                    views.RedemptionCode]

    .. py:attribute:: base_pay = models.PositiveIntegerField()
    
        How much each Participant is getting paid to play the game
        
    .. py:attribute:: participants_per_match
    
        Class attribute that specifies the number of participants in each match. 
        For example, Prisoner's Dilemma has 2 participants.
        a single-participant game would just have 1.

    .. py:method:: matches(self):
    
            The matches in this treatment. Syntactic sugar for ``self.match_set.all()``


Experiment
~~~~~~~~~~
Coming soon. (You will not be using this object frequently.)
