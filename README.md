# Diamond Exchange

This project attempts to develop a web app for Jehovah's Witnesses that will facilitate interactive learning through AI- and social networking-enhanced learning experiences, including some of the following features:

* Study adventures: personalized recommendations for one's study based on current reading history, study objectives, estimated current knowledge, and other data users share with the web app, attempting to engage students fully with their learning.
* Social networking: spiritual gems are meant to be shared (Matthew 12:35); in turn, doing so can bring great joy. Social networking features could perhaps facilitate the rate of spread of such gems, like those shared during the *Digging for Spiritual Gems* section of the midweek meetings.
* Witnessing simulator: Practice can help sharpen one's skills, and AI language models may be capable of giving realistic feedback for witnessing simulations. The witnessing simulator would notice, commend, and recommend to students how they can improve in the ministry and on the platform.

Perhaps more features could be added. More details on these features to be written.

## Components

Central to this project is a "teacher AI" system capable of reasoning on learning outcomes and teaching devices (statement of fact, illustration, narrative, etc). It would need to be able to estimate the learning impact that a teaching device has for a student; it would need to be able to search for teaching devices that meet given learning outcome requirements, and it would need to do this efficiently; it may not be feasible to include AI language model (requests?) with every teaching action. See the [current source](./src/ai/).

The "learning adventures" feature would use this to discern what direction of study a student is learning towards and how it may help them best.

The social networking features may supply gems to enhance a person's study, and it may use this system to have additional moderation of content value.

The witnessing simulator would use the AI system to simulate a teacher directly or to evaluate a real teacher's performance as a teacher and commend and recommend how they may improve.

Currently this project has just started being developed in python (previous TypeScript/T3 approach spent much time on boilerplate). This python implementation may use the following stack:

* Front end developed with bubble.io (not yet started)
* Controller layer of a python FastAPI server
* Database hosted on cloud service provider and accessed through python server
* AI language models and retrievers organized with DSPy, perhaps also LlamaIndex

## Development

Contributors are welcome.
