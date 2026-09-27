---
title: "Data Governance: When Does It Actually Help?"
date: 2026-09-26
category: "Data Leadership"
tags:
  - Data Leadership
  - Leadership
  - Data Governance
  - Communication
  - Personal Development
description: "Some thoughts from a technical data perspective on what data governance is actually trying to achieve, and when it becomes bureaucracy instead."
featured: false
---

I've been thinking quite a bit more about data governance recently, inspired by the C&J course and because we are constructing some interesting access and security requirements at work. 

The more I learn about data strategy and leadership, the more I realise that there are quite a lot of questions around governance that I haven't really thought about properly before.

And, if I'm honest, the word **governance** has never been particularly exciting to me. 

As someone who has spent a lot of my career working on the technical side of data, governance can sometimes sound like more meetings, more documentation, more approvals and more people telling you that you can't do something.

## So what actually is data governance?

My current, fairly simple, way of thinking about it is that governance is about making sure we know:

* What our data means
* Who owns it
* Who is responsible for it
* Who can change it
* Who can use it
* How much we trust it
* What happens when something goes wrong

None of that sounds particularly controversial.

The problem is what happens when you try to implement it.

## Governance or bureaucracy?

I think there is a fairly fine line between the two.

You can have a process that says:

> "This change requires approval from X, Y and Z."

That might be governance.

Or it might just be bureaucracy.

The difference, for me, is whether the process actually helps us manage a meaningful risk or make a better decision.

If I have to fill in a form because the process says I have to fill in a form, but nobody uses the information on the form to make a decision, I'm not sure that's governance.

Whereas if I know who owns a piece of data, what it means, how important it is and what happens if it is wrong, that feels much more useful.

I think of good governance as something that should make the right thing easier, rather than simply making change harder.

## The technical person's perspective

This is probably where my own background influences how I think about this. As a data engineer, you often end up seeing the consequences of poor governance quite a long way down the line. You might get a requirement to produce a report and discover that two systems have completely different definitions of the same thing.

- Or nobody knows who owns a particular field. Always fun when transactional systems get new columns and nobody tells the warehouse team. 
- Or there are three versions of what is supposedly the same dataset. Normally cause different stakeholders have slightly different rules but think all the numbers should match up... and funnily enough they don't. 
- Or a transformation contains some business rule that was added years ago and nobody can explain why it exists. We always try and document these things but when you are on your 3rd version of a warehouse there can be legacy rules that just exist... because.
- Or everyone agrees that a number is wrong, but nobody is quite sure who is responsible for fixing it. This one rarely happens with me as with my subject area it will almost always be my team... unless the source system in wrong or they have calculations in the front end reports... so maybe not so simple.

At that point, it's very tempting to solve the problem technically.

- Add another transformation. Cause you can never have enough notebooks.
- Add another lookup. Ah another static look up to maintian. 
- Add another exception. Surely hard coded. 
- Put another rule into the pipeline. And forget it is there!

And sometimes that is exactly what you need to do. But sometimes you're just putting another layer of code on top of an organisational problem. That's where I think governance becomes much more interesting.

## The problem with fixing governance in the pipeline

One thing I've increasingly noticed is that by the time a governance problem reaches a data engineer, we're often already quite far down the road.

The business hasn't agreed what something means. Nobody has formally agreed ownership. The source system doesn't enforce a particular rule, certainly had this one! So the data team ends up implementing the rule and boy do you end up going round the houses to get things to work sometimes.

And now the pipeline knows something that the organisation itself hasn't necessarily agreed or isn't fully documented somewhere. This can work.

Until somebody asks:

> "Why does the pipeline do that?"

And the answer is:

> "Because that's what we were told to do five years ago." (can't think of any examples but probably a true story)

That's not a particularly comfortable place to be. It also makes changing things harder.

The technical implementation can become the de facto source of truth for a business rule and when you are working in a warehouse that is supposed to use the business rules from the transactional system....

## Should everything be governed equally?

I don't think everything needs the same level of governance.

A critical financial figure used for external reporting probably needs a very different level of control from an experimental dataset that an analyst has created to investigate an idea. Both are data. But the consequences of getting them wrong are very different. I would also hope the POC doesn't make it into Prod without sign off and control. 

So governance needs to be proportional to things like:

* Risk
* Importance
* Sensitivity
* Number of people relying on the data
* Regulatory requirements
* Business impact

That seems much more sensible to me than trying to apply exactly the same governance process to everything.

## Can governance help people move faster

This is probably the bit I'm still working through. It is easy to think of governance as something that slows things down, and sometimes it certainly feels that way. 

You have a new idea.

You want to build something.

Governance says:

> "Hang on. You need to go through this process first."

But good governance could potentially have the opposite effect.

If I already know:

* Who owns the data
* What the data means
* Where it comes from
* What I'm allowed to do with it
* How reliable it is
* What controls are required

then I can actually get on with building something.

The decisions have already been made.

## Conclusion

Those are some of the things I'm interested in exploring as I learn more about data strategy and leadership.

Data governance shouldn't be about putting obstacles in front of people and techy people shouldn't view it in that light. 

It should be about creating enough clarity that people can use data confidently and make better decisions.

And if it does that, perhaps governance isn't the boring bit of data after all.
