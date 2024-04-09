# Diamond Exchange

This project attempts to develop a web app for Jehovah's Witnesses that will facilitate interactive learning through AI- and social networking-enhanced learning experiences, including some of the following features:

* Study adventures: personalized recommendations for one's study based on current reading history, study objectives, estimated current knowledge, and other data users share with the web app, attempting to engage students fully with their learning.
* Social networking: spiritual gems are meant to be shared (Matthew 12:35); in turn, doing so can bring great joy. Social networking features could perhaps facilitate the rate of spread of such gems, like those shared during the *Digging for Spiritual Gems* section of the midweek meetings.
* Witnessing simulator: Practice can help sharpen one's skills, and AI language models may be capable of giving realistic feedback for witnessing simulations. The witnessing simulator would be an online platform for students to practice preaching and teaching with a simulated environment; an AI system could then commend and recommend to students how they may improve in the ministry.

Perhaps more features could be added. More details on these features to be written.

## Components

Central to this project is a "teacher AI" system capable of reasoning on learning outcomes and teaching devices (statements of fact, illustrations, narratives, simulations, questions, etc). It must estimate the learning impact that a teaching device has for a student and must be able to search for teaching devices that meet given learning outcome requirements. It would need to do this efficiently; it may not be feasible to include AI language model requests with every teaching action. See [progress of current implementation](./src/ai/).

The "learning adventures" feature would use this to discern what direction of study a student is learning towards and how it may best help them.

The social networking features would use this in recommending content, and it may use this system to moderate submitted content.

The witnessing simulator would use the AI system for simulating a teacher directly and for evaluating a real teacher's performance, to offer commendation and recommendation for improvement.

Currently this project has just started being developed in python (a previous TypeScript/T3 approach spent too much time on boilerplate). This python implementation may use the following stack:

* Front end developed with bubble.io (to be started)
* Controller layer of python FastAPI server
* Database hosted on cloud service provider and accessed through python server
* AI language models and retrievers organized with [DSPy](https://dspy-docs.vercel.app/), perhaps also LlamaIndex

## Development

Contributors are welcome.
