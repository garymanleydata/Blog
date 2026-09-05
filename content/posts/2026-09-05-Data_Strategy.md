---
title: "Data Strategy: From Strategy to Practice"
date: 2026-09-05
category: "Data Strategy"
tags:
  - Data Strategy
  - Data Engineering
  - Data Leadership
description: "Some thoughts on Data Strategy, what I am learning from the Summer School, and how I can apply it as a Data Lead."
featured: false
---

## What is a Data Strategy and Why is it Important?

What is a Data Strategy?

In *The Chief Data Officer's Playbook* and the Summer School curriculum, Caroline Carruthers and Peter Jackson define a data strategy as:

> "A Data Strategy is a clear, actionable plan for all aspects of data within your organisation that directly underpins the overarching business strategy."

I think this is a useful starting point.

A data strategy is not an isolated IT roadmap, a technology shopping list, or a thousand-line Gantt chart. Nor is it a static, bound document destined to gather dust on an executive bookshelf.

Instead, a true data strategy is a living, multi-dimensional framework that defines how an organisation treats data as a strategic corporate asset, how it manages the balance between risk and value, and how it transforms human behaviours across functional silos.

At its simplest, I think about it something like this:

```text
┌────────────────────────────────────────┐
│       OVERARCHING BUSINESS STRATEGY    │
│                                        │
│   Commercial, Operational, Statutory   │
└───────────────────┬────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────┐
│             DATA STRATEGY              │
│                                        │
│  ┌──────────────┐    ┌──────────────┐  │
│  │ PURPOSE      │    │ PEOPLE       │  │
│  │ Strategy,    │    │ Skills,      │  │
│  │ Risk,        │    │ Behaviour,   │  │
│  │ Governance   │    │ Leadership   │  │
│  └──────────────┘    └──────────────┘  │
│                                        │
│  ┌──────────────┐    ┌──────────────┐  │
│  │ METHOD       │    │ TOOLS        │  │
│  │ Organisation,│    │ Architecture,│  │
│  │ Framework,   │    │ Metrics,     │  │
│  │ Policies     │    │ Technology   │  │
│  └──────────────┘    └──────────────┘  │
└────────────────────────────────────────┘
```

What I've been thinking about recently, particularly through the Summer School, is less about **what a data strategy is** and more about **what this actually means in practice**.

Especially when you are not the Chief Data Officer or the person responsible for the organisation-wide strategy.

What can I actually influence as a Data Lead?

---

## Data Strategy and Technology Strategy

There is obviously a relationship between data strategy and technology strategy, but I think it is important not to confuse the two.

**Technology strategy asks:**

* What platform should we use?
* Lakehouse or warehouse?
* What tools do we need?
* How do we modernise our architecture?
* How do we scale?
* What should we automate?

These are the sort of decisions that I am used to being involved in and used to having fun with.

But a data strategy asks some different questions.

**Data strategy asks:**

* What decisions do we need to make better?
* What data do those decisions depend upon?
* Who owns that data?
* What does "good" data mean?
* Which data matters most?
* Where are our biggest risks?
* What capabilities do we need?
* How mature are we today?
* What should we *stop* doing?
* What value are we actually trying to create from our data?

These help us understand **why we are making those technology decisions in the first place**.

There is also a question that I think is particularly useful for a data team:

> **What are we building because it creates value, and what are we building because we can?**

That is not always an easy question to answer.

---

## A Data Strategy Doesn't Have to Be One Thing

One of the ideas from the Summer School that I have found particularly interesting is the idea that a singular data strategy doesn't necessarily have to cover everything in exactly the same way.

There will always be urgent decisions that need to be made.

There may be a burning issue that needs addressing quickly, while at the same time the organisation needs to think about its intermediate goals and its longer-term target state.

Trying to create one enormous strategy that solves everything at once doesn't necessarily make sense.

You might instead have:

```text
┌─────────────────────────────────────┐
│          IMMEDIATE PRIORITIES       │
│                                     │
│  What needs fixing or deciding now? │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│       INTERMEDIATE CAPABILITIES     │
│                                     │
│  What do we need to develop next?   │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│           TARGET STATE              │
│                                     │
│  Where do we ultimately want to be? │
└─────────────────────────────────────┘
```

This feels much more practical to me.

A strategy needs to provide direction, but it also needs to recognise the reality of the organisation today.

---

## What Makes a Good Data Strategy?

A data strategy cannot exist in a vacuum.

If a business strategy focuses on improving patient outcomes or reducing customer churn, the data strategy must explicitly detail how data collection, quality and modelling make those specific outcomes achievable.

If the business strategy is vague or missing, a data leader cannot simply "sit on their hands" — they need to actively engage executive colleagues to help define the desired business outcomes.

I also think a good data strategy needs to be **succinct and authentic**.

It should avoid overly complex technical jargon.

An effective strategy should be something that can be articulated in an elevator pitch and distilled into memorable principles that win over the board and operational teams.

I work in the public sector, and one thing I am particularly conscious of is that we already have no shortage of acronyms, frameworks and governance structures.

We don't necessarily need another layer of complexity simply for the sake of appearing strategic.

A strategy needs to be understandable to the people who are expected to work with it.

For me, a good data strategy should therefore be:

**Business-led**

It should start with organisational outcomes rather than technology.

**Understandable**

People should be able to explain what it means without needing a glossary.

**Prioritised**

Not all data is equally important, and not every dataset requires the same level of investment.

**Pragmatic**

We don't necessarily need to fix everything before we can start delivering value.

**Living**

The strategy needs to change as the organisation, technology, risks and priorities change.

---

## From Strategy to Practice

This is probably the area I have been thinking about most.

I am currently a Data Lead, but I don't need to own the organisation's entire Data Strategy to influence how data is managed.

I can still determine the strategy of my team and define our goals and targets with best practice and data governance in mind.

Many of the things that I think are important probably seem obvious.

But when teams are busy and deadlines are approaching, shortcuts are often taken.

We try to focus on making sure our code is documented, thoroughly tested, follows our standards and best practice, and we try to enforce those values into everything we do.

These aren't necessarily revolutionary ideas.

But perhaps strategy isn't always about discovering something nobody has thought of before.

Sometimes it is about deciding what matters and then being consistent enough to do those things well.

I think there is a useful relationship here:

```text
DATA STRATEGY
      │
      ▼
PRINCIPLES
"What do we believe?"
      │
      ▼
PRACTICES
"What do we actually do?"
      │
      ▼
OUTCOMES
"What difference does it make?"
```

For example:

### Principle

Data products should be trustworthy.

### Practice

Pipelines should have appropriate automated data-quality checks, testing and documentation.

### Outcome

Consumers can use the data with greater confidence.

Or:

### Principle

We should build reusable solutions rather than repeatedly solving the same problem.

### Practice

Common ingestion, transformation and deployment patterns are standardised.

### Outcome

Delivery becomes faster, more consistent and easier to maintain.

This is where I think data strategy starts becoming much more tangible.

---

## Data Quality

The other thing I think of as particularly important is **data quality**.

It is easy to think of data quality as an engineering problem.

Does the pipeline run?

Did the notebook complete successfully?

Did the table load?

Did the job turn green?

But a successful pipeline doesn't necessarily mean that the data is good.

The data could still be:

* incomplete
* inaccurate
* duplicated
* inconsistent
* invalid
* out of date
* missing important business context

And perhaps the more important question is:

> **Who decides what "good enough" means?**

That is not necessarily a technical decision.

A dataset supporting a statutory report may require a very different level of assurance from a dataset being used for exploratory analysis.

Data quality therefore isn't simply about adding more validation rules.

It is about understanding what the data is being used for, what the risks are, who owns it and what level of quality is actually required.

A technically perfect pipeline delivering the wrong business data is still a failure.

---

## Governance Should Be Part of Engineering

This also changes how I think about data governance.

Governance can sometimes feel like something that happens around the edges of data engineering.

Policies are written.

Standards are documented.

Governance meetings happen.

People are assigned ownership.

But many of those principles can actually be built into the way we engineer data.

- Documentation.
- Testing.
- Naming standards.
- Metadata.
- Lineage.
- Data-quality checks.
- Monitoring.
- Clear ownership.
- Reusable patterns.

These aren't just engineering hygiene.

They are ways of putting data governance into practice.

What I have really enjoyed on a recent data migration project is baking these ideas and concepts in from the start. We came up with the standards and guidance as a team, documented it and then stuck to it. 

---

## What Should We Stop Doing?

One question from the data strategy discussion that I particularly like is:

> **What should we stop doing?**

Data teams often focus on what we should build. But strategy also requires us to decide what isn't worth doing.

Perhaps there are reports that nobody uses. Data that nobody trusts. Manual processes that should have been retired years ago, or that could be easily automated. Multiple versions of essentially the same dataset. Pipelines that exist because of an old requirement that no longer exists. Or perhaps we are building increasingly complicated solutions because nobody stopped to challenge the original requirement.

Stopping something can be just as strategic as starting something.

---

## What I'm Taking Away

The biggest thing I am taking away from the Summer School, on strategy, isn't another framework or another definition of data strategy.

It is thinking more about how the strategy translates into the everyday decisions made by data teams.

I still enjoy the technology side of data. I always will. I enjoy thinking about architecture, platforms, pipelines, automation and how we can build things better.

But I am increasingly interested in what sits alongside and before those things:

* What problem are we actually trying to solve?
* What value are we trying to create?
* What data do we need?
* What does good look like?
* What are the risks?
* Who owns it?
* What capabilities do we need?
* What should we stop doing?

I don't think I have suddenly become an expert in Data Strategy. What I do think is that I am starting to see how I can contribute to it. It can be reflected in the standards we set, the questions we ask, the things we build, the things we don't build, and the behaviours we encourage within our teams.

And for me, that's where the theory of Data Strategy starts becoming much more interesting.
