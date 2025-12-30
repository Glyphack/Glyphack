---
title: "Devlog 6: I Can Make a CPU with My Logic Gate Simulator"
date: 2025-12-21T21:43:56+01:00
draft: false
tags: [] 
---

I can finally start making a CPU using [my logic gate simulator](https://github.com/Glyphack/simu).

Try it yourself [here](https://glyphack.github.io/simu/)!

It supports basic things you expect from a logic gate simulator.
Drag gates onto the canvas.
Attach them together using wires.
Wires stick to pins like magnets.
You can detach a wire by selecting it and then move it.

{{< video src="/simu-1.mp4" type="video/mp4" >}}

You can create a connection between two gates by dragging a pin to another.
When a wire is connected to a gate it stays connected even if the gate moves.
Moving a wire detaches it from its connections.
A wire can be split into two. A new wire is drawn from the middle, which you can connect elsewhere.
You can select gates to move them around.
When you select things you can use copy and paste for each instance.

Simulator is simple and it runs real-time.
It supports feedback loops.
You can build memory circuits like [Flip Flops](https://en.wikipedia.org/wiki/Flip-flop_(electronics)).

{{< video src="/simu-2.mp4" type="video/mp4" >}}

The next feature that I needed was a way to create circuits.
A CPU contains thousands of similar circuits. Like Registers.
In Simu you can select gates and create a module from them.
The module input/output is mapped to input/output pins that are unconnected.

{{< video src="/simu-3.mp4" type="video/mp4" >}}

To create a module you need to first free up some pins.
Free pins are what is considered input/output of the module.

The module behaves as if those gates were placed directly in the circuit.
Modules are note special.
Whenever a module is created the state of its gates and connections is saved and when it's added to the circuit the members of the module are added to the circuit.
Connecting something to the module is similar to connecting it to what's inside the module.
I made this decision to make modules easier to integrate with rest of the code.
This makes it possible to be able to see what exactly is happening in the module. Live as the simulation is running.
Modules are just a faster way to place multiple gates with their connections in the circuit.
It's also possible to view inside modules and the state of internal gates.

The panel on the left side and the debug logs window are development tools.
They provide everything that is happening in the app on the screen to [walk around](https://bernsteinbear.com/blog/walking-around/) the app.

That's all there is to the UI.
The Rest of it are small functionalities to create a circuit faster.
The next part is about the design and code of the application

---

## References Using IDs

The main struct in Simu is DB. It holds all the objects on the space and looks like this:

```rust
#[derive(Default, serde::Deserialize, serde::Serialize, Debug, Clone)]
pub struct Circuit {
    // Type registry for each instance id
    pub types: SlotMap<InstanceId, InstanceKind>,
    // Per-kind payloads keyed off the primary key space
    pub gates: SecondaryMap<InstanceId, Gate>,
    pub wires: SecondaryMap<InstanceId, Wire>,
    pub connections: HashSet<Connection>,
    ... Rest of the objects
}

```

[source](https://github.com/Glyphack/simu/blob/35177cdb0dbabd1ec884a8331cfb70233a4d628d/src/db.rs#L60)

[Slotmap](https://docs.rs/slotmap/1.1.1) is similar to an array.
Upon inserting a new instance it returns an ID and that's why everything is a map from `InstanceId` to the actual data.
Everything in the program refers to other things using the ID.

Connections just hold some IDs of which pins from what ID are connected.

```rust
pub struct Connection {
    pub a: Pin,
    pub b: Pin,
    pub kind: ConnectionKind,
}

pub struct Pin {
    pub ins: InstanceId,
    pub index: u32,
    pub kind: PinKind,
}
```

[source](https://github.com/Glyphack/simu/blob/35177cdb0dbabd1ec884a8331cfb70233a4d628d/src/connection_manager.rs#L20)

As an example to get to instances connected to a pin with this data structure we have to:

1. Find connections including that pin
2. Get the other pin in those connections
3. Get the instance ID of those pins
4. Find what is the type of that instance ID
5. Lookup the instance ID in its associated map(wires, gates, etc.)

This is harder to do than having objects embedded into each other and having access like `pin.instance.pos`.
But it introduces borrow checker issues.
Which is painful to deal with. And requires a lot of code.

In this program I know when and where something is not needed and how to clean up the object.
I don't have anything against smart pointers, my reasoning was similar here: I know when and how the clean up should happen I can just code it.
If I had a more complex object lifetime then I could consider them.

Another major benefit of using IDs is being able to save and load circuits easily.
There's almost no serialization code to persist state of the program to the disk.

## Simulation Logic

Simulation logic is straightforward except for feedback loops.
Let me explain.

In some circuits we feed the output of the circuit back to itself.
This is for creating "memory" so the circuit works based on its previous state.
What happens in these circuits is this:

1. Gate A output is connected to Gate B
2. Gate B output is connected to Gate A

Now in order to calculate the output of Gate A we need to calculate Gate B.
One solution here is to assume a fallback value for output of Gate A and then we can calculate Gate B.
Once B is determined we use that to calculate A.
But we are not done yet. We assumed a fallback value for A.
Now that we have fallback value of A output and calculated value we need to compare them.
If the computed value is different from the assumption then we need to redo the computation this time with the new computed value.
This operation goes on until the value we get out of computing is same as what we assumed at the beginning.
Is it guaranteed to get to this point? Well no, you can connect output of a NAND to itself.
This causes the gate output to toggle between on and off.

Following the same algorithm above:

1. Assume output is 0
2. Input is 0
3. NAND with 0 input is 1 -> contradicts assumption

No matter how many times we iterate, a NAND connected to itself is going to toggle.
So we need an upper bound of times we try to iterate to get to a stable point.
This number is 10 in the program.
Meaning that the program will simulate the whole circuit at most 10 times and check if the cycles are resolved.
Note that this only happens when there is complex cycle in the program, most of cycles resolve in 6 or 7 iterations.
My plan for more optimization here is to resolve each cycle in isolation.
This will require [SCC](https://en.wikipedia.org/wiki/Strongly_connected_component).
This means that if a cycle contains 5 instances out of 100 in the circuit only those 5 would be re computed multiple times.

---

I always wanted to try making a better logisim.
That was the program I used as a student to make a 16-bit CPU based on [Mano's book](https://www.goodreads.com/book/show/224131.Computer_System_Architecture).
That software is good but it's not fast and responsive. It does not run in the browser and the UI is not good.

My first goal is to start making my own CPU. Along the way I discover more UI features that I need to make it faster and better.
And after that maybe I can add a way to design quizzes.
It would be fun to solve puzzles for learning logic gates.
I wish more things were interactive when I was learning.
But I can build them for others.
