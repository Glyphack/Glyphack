---
title: "Huec"
date: 2026-02-25T22:25:08+01:00
draft: true
tags: [] 
---

For a long time I was looking for a way to control my Phillips light strip.
I searched and what came up was controlling the lamp with Hue bridge.
That's the normal way to control a smart Phillips lamp.
But I don't want to buy another device from this company that keeps its stuff undocumented and release a shitty app.

So while I was waiting for the light to die slowly and then replace it with another light. I found something that "inspired" me to do something.

I found this tool blendr(todo link) that can connect to low energy Bluetooth devices. (todo maybe more explain.)

So after installing it(didn't work on rust 1.90 downgraded 1.79)
I started looking into my lights.
I found a couple of values that where written into characteristics.
These values were controlling the state of the lamp.
I took my phone and turned it on and then off and checked the characteristics and I found one that was related to the turning on and off.

Next I searched how can I control this programmatically.
I found a library called Bleak.

Then I wrote some code to write 0x01 and 0x00 into that characteristic and tried it.
And it turned the light on and off!
It was huge. It means that I can use my computer to control the light.
I don't need to use the shitty app anymore.

My goal was to have a workflow like this:

- Turn on/off the light form computer. For when I'm sitting on the desk and don't want to grab my phone. Also it's nice to be able to set brightness and color.
- Turn on the light in the morning when I wake up and turn off when the sun is up.

The first functionality is almost done. I can turn the light on and off but how do I change the color?

## Color

I looked around in the characteristics and tried out all the characteristics below the on/off one.
todo: list them.

You can easily find out the pattern by changing the light color and observing the characteristic values.
There are multiple characteristics that change when you change the light color:
- todo changes with brightness
- todo changes with color (if I do warm white then cool white stays the same)
- todo changes with everything.

The third option is more general hence more useful.
The value inside of it looks like this:

```
cool white:
0x01,0x01,0x01,0x02,0x01,0xFE,0x03,0x02,0x9C,0x00
warm white:
0x01,0x01,0x01,0x02,0x01,0xFE,0x03,0x02,0x5a,0x01
```

It's clear that `FE` is the brightness. it's 254.
For some reason you cannot set the brightness to 255 and this is the limit.
The byte before the last one is controlling the todo: kelvin.

The initial bytes until brightness byte seem to be constant. It does not change. with different things I tried.
todo: verify

There are two bytes between the brightness and warmness.
`0x03,0x02` seem to be only the case for white color.

When I set it to another color the bytes change to this format:
```
0x01,0x01,0x01,0x02,0x01,
brightness,0x04,0x04,
color byte 1, color byte 2,
color byte 3, color byte 4
```

The number of bytes increase.
So we have 4 bytes in total to set the color.

I haven't dug deeper. I gave some examples to perplexity and it informed me that the color is encoded in **CIE 1931 xy chromaticity** format.
So I skipped this part for now. my goal was not to control the light exactly. This was just a side quest.

## Timer

Then I started looking into timers.
Timers was the ultimate goal for me. I wanted my light to turn on every day.
But turning on using the on and off command meant that I have to have some device controlling the light.

I started looking into other characteristics and I didn't find anything related timers.
Characteristics have multiple kinds. For color and power they are read and write.
Meaning that you can write to it and you can read from it.
But there are also characteristics with notify option.
Which you can write to and get notification from it.

So for this I needed to see what my phone was doing to set the alarms.

Well The good news is that there is a software from Apple called Packet Logger.
Which can be downloaded from [Bluetooth - Apple Developer](https://developer.apple.com/bluetooth/).
You need an apple account to download it.
I hate this because when I was in Iran any of these tools was blocked because you can't easily open an account.
But I'm now upgraded and live in a place where I am allowed to open an account so I have it.
So I went ahead and downloaded that you also need a profile to install on IOS.
You can get it [Profiles and Logs - Feedback Assistant - Apple Developer](https://developer.apple.com/feedback-assistant/profiles-and-logs/).

Install packet logger on computer and the profile on an iPhone and then connect the phone to computer and start working with the app and you would see the packets coming and going.

So I started checking what the application does when I connect to the light.
I found the following requests:

```
Feb 12 12:10:23.743  ATT Send         0x005A  Hue lightstrip pl  Write Request - Handle:0x0068 - Value: 0311 00  
	Write Request - Handle:0x0068 - Value: 0311 00
	Opcode: 0x12
	Attribute Handle: 0x0068 (104)
	Value: 0311 00
Feb 12 12:10:23.743  L2CAP Send       0x005A  Hue lightstrip pl  Channel ID: 0x0004  Length: 0x0006 (06) [ 12 68 00 03 11 00 ]  
	Channel ID: 0x0004  Length: 0x0006 (06) [ 12 68 00 03 11 00 ]
	L2CAP Payload:
	00000000: 1268 0003 1100                           .h....
Feb 12 12:10:23.743  ACL Send         0x005A  Hue lightstrip pl  Data [Handle: 0x005A, Packet Boundary Flags: 0x0, Length: 0x000A (10)]  
Feb 12 12:10:23.789  ATT Receive      0x005A  Hue lightstrip pl  Write Response  
	Write Response
	Opcode: 0x13
Feb 12 12:10:23.789  L2CAP Receive    0x005A  Hue lightstrip pl  Channel ID: 0x0004  Length: 0x0001 (01) [ 13 ]  
	Channel ID: 0x0004  Length: 0x0001 (01) [ 13 ]
	L2CAP Payload:
	00000000: 13                                       .
Feb 12 12:10:23.789  ACL Receive      0x005A  Hue lightstrip pl  Data [Handle: 0x005A, Packet Boundary Flags: 0x2, Length: 0x0005 (5)]  
Feb 12 12:10:23.789  ATT Receive      0x005A  Hue lightstrip pl  Handle Value Notification - Handle:0x0068 - Value: 0300 1100  
	Handle Value Notification - Handle:0x0068 - Value: 0300 1100
	Opcode: 0x1B
	Attribute Handle: 0x0068 (104)
Feb 12 12:10:23.789  L2CAP Receive    0x005A  Hue lightstrip pl  Channel ID: 0x0004  Length: 0x0007 (07) [ 1B 68 00 03 00 11 00 ]  
	Channel ID: 0x0004  Length: 0x0007 (07) [ 1B 68 00 03 00 11 00 ]
	L2CAP Payload:
	00000000: 1B68 0003 0011 00                        .h.....
Feb 12 12:10:23.789  ACL Receive      0x005A  Hue lightstrip pl  Data [Handle: 0x005A, Packet Boundary Flags: 0x2, Length: 0x000B (11)]  
Feb 12 12:10:23.791  ATT Receive      0x005A  Hue lightstrip pl  Handle Value Notification - Handle:0x0068 - Value: 0411 00FF FF  
	Handle Value Notification - Handle:0x0068 - Value: 0411 00FF FF
	Opcode: 0x1B
	Attribute Handle: 0x0068 (104)
Feb 12 12:10:23.791  L2CAP Receive    0x005A  Hue lightstrip pl  Channel ID: 0x0004  Length: 0x0008 (08) [ 1B 68 00 04 11 00 FF FF ]  
	Channel ID: 0x0004  Length: 0x0008 (08) [ 1B 68 00 04 11 00 FF FF ]
	L2CAP Payload:
	00000000: 1B68 0004 1100 FFFF                      .h......
Feb 12 12:10:23.791  ACL Receive      0x005A  Hue lightstrip pl  Data [Handle: 0x005A, Packet Boundary Flags: 0x2, Length: 0x000C (12)]  
	Packet Boundary Flags: [10] 0x02 - First Flushable Packet Of Higher Layer Message (Start Of An L2CAP Packet)
	Broadcast Flags: [00] 0x00 - Point-to-point
	Data (0x000C Bytes)
Feb 12 12:10:23.791  ACL Receive      0x0000  00:00:00:00:00:00  00000000: 5A20 0C00 0800 0400 1B68 0004 1100 FFFF  Z .......h......  
Feb 12 12:10:23.959  HCI Event        0x005A  Hue lightstrip pl  Number Of Completed Packets - Handle: 0x005A - Packets: 0x0001    
	Parameter Length: 5 (0x05)
	Number Of Handles: 0x01
	Connection Handle: 0x005A
	Number Of Packets: 0x0001
```

I had a good run with [perplexity](https://www.perplexity.ai/search/how-to-capture-the-ble-writes-bsgCtVUHQKqln9khE5Hh7w) helping me in this whole investigation(todo: I don't like this word).
It told me what to do and then figured out how the app gets the timers.
You might notice that there is no trace of characteristic uuids here.
I searched around and didn't find a way to map the handle that I see in the logs to uuid.
So I did what a sane person would do and stopped spending more time.
I just brute forced my way by sending the same message to every characteristic and see which one responded back.
That's how I got the one.

Here's the breakdown. The timer characteristic (todo uuid) is like a server.
You can write different messages to it and subscribe to it to get back responses as notifications.
When the app connects the first packet is:
```
0x00
```

Then the application responds back the list of IDs for the alarms that are already set:
```
00 00 00 03 | ID0_lo ID0_hi | ID1_lo ID1_hi | ID2_lo ID2_hi
```

The `03` is the number of alarms.

So it's basically like a CRUD app.
Next is to read the alarm details using its id.

We construct this message:
```
0x02, lo, hi, 0x00, 0x00
```

Which gives us the full alarm details.

Now we have a bit of decoding to do here.
The way I did this was by setting up a lot of alarms and seeing how the change the payload.
In the end I didn't fully decode what this payload means. For me the goal was to enable an alarm every day.
That's what I did.

Let's look at one example:

```
02 00 2c 00 35 00 00 00 00 01 00 60 55 95 69 00
09 01 01 01 06 01 09 08 01 7d 22 01 d4 0c 13 8d
81 b9 4a 4c aa 42 b9 9a ce c6 2d 88 00 ff ff ff
ff 0a 4d 6f 72 6e 69 6e 67 20 75 70 01
```

Here's what I found out:
1. `02 00` is saying that this response is for alarm info.
2.  `0x002C` is the alarm ID.
3. `0x35` is length of the payload.
4. The `0100` before the `60`... is the alarm active state.
5. `60 55 95 69` is the timestamp for the alarm in little endian format which is 2026-02-16 6:00.
6. Then you have a series of bytes that I don't know what they are related to, we call them mystery bytes.
7. Then you have `ff ff ff ff` which I think is a separator for the alarm info and the name. I verified it by sending `00 00 00 00` instead and seems like the lamp ignores it.
8. Then you have the name `0a 4d 6f 72 6e 69 6e 67 20 75 70 01` length + characters + `01`

That's it. You can read and parse the alarm.

Can we create any alarm we like now?
No, I tried this, the problem is that the magic bytes seem to have a special meaning.
When I took this same message and just tried to create random alarms by substituting my timestamp and name the lamp was not creating the alarm.

From my investigation I found this is the packet that the app uses to create alarm.

```
01FF FF00 0100 D8B6 8E69 0009 0101 0106 0109 0801 5B19 0194 D184 84B7 5143 DAA8 67A9 2F02 110C 8D00 FFFF FFFF 0141 01
```

1. `01FF` is the command to create a new alarm.
2. `0100` tells the alarm is active.
3. `D8B6 8E69` is timestamp in little endian format.
4. `0009 0101 0106 0109 0801` hasn't change I guess it's related to the effect (here it's "sunrise").
5.  `5B19 0194 D184 84B7 5143 DAA8 67A9 2F02 110C 8D00` mystery bytes.
6. After `0141 01` separator it's name of the alarm.

After alarm write is success there will be these two notifications which reply back with the ID of the alarm.
It's useful to verify the right actually happened. But I didn't get any extra information from it.

```
0100 FFFF 1E00
```

```
04FF FF1E 00
```

Then I tried making the same alarm twice with everything and here's the result:

```
01FF FF00 0100 305C 9169 0009 0101 0106 
0109 0801 651F 01FB D061 C25B 6340 F6AA 
71BB 49E1 86F0 C900 FFFF FFFF 0757 616B 
6520 7570 01

01FF FF00 0100 305C 9169 0009 0101 0106 
0109 0801 651F 0185 97FE 881C C146 47A1 
9D9F 6A8C 2C29 7B00 FFFF FFFF 0757 616B 
6520 7570 01
```

---
Then I tried turning alarms on and off. My plan was to see if I can just make the alarm with my phone and then enable it with the computer that would work too.

Here's the packets for that.
What I did here was turning the alarm on and off and check the alarm by querying the alarm detail the way I explained above with the timer characteristic.

```
Created alarm with state on:

	Value: 01FF FF00 0100 D8B6 8E69 0009 0101 0106 
	0109 0801 5B1C 0134 A261 1076 CA45 7FA7 
	E50B F7F3 9063 7200 FFFF FFFF 0457 616B 
	6501

off:

	Value: 010E 0000 0000 D8B6 8E69 0009 0101 0106 
	0109 0801 5B1C 0134 A261 1076 CA45 7FA7 
	E50B F7F3 9063 7200 FFFF FFFF 0457 616B 
	6500

on:
	Value: 010F 0000 0100 D8B6 8E69 0009 0101 0106 
	0109 0801 5B1C 0134 A261 1076 CA45 7FA7 
	E50B F7F3 9063 7200 FFFF FFFF 0457 616B 
	6501

off:
	Value: 0110 0000 0000 D8B6 8E69 0009 0101 0106 
	0109 0801 5B1C 0134 A261 1076 CA45 7FA7 
	E50B F7F3 9063 7200 FFFF FFFF 0457 616B 
	6500

```

Notes here:

1. The alarm ID is increasing every time it is edited. But it's the responsibility of the lamp to assign the ID.
2. the 5th byte is active/deactivate info.

So I did this experiment to be sure what happens to the light:

Experiment create a new alarm:

```
Value: 01FF FF00 0100 4089 9069 0009 0101 0106 
0109 0801 651C 01EF 5572 FEF8 174B 67AC 
ED26 721F CFAA 2400 FFFF FFFF 0454 6573 
7401
```

```
Handle Value Notification - Handle:0x0068 -Value: 0100 FFFF 0100
```

```
Handle Value Notification - Handle:0x0068 - Value: 04FF FF01 00
```

After alarm went off this is the alarm payload using read alarms:

```
02 00 06 00 2f 00 00 00 00 00 00 c0 da 91 69 00 09 01 01 01 06 01 09 08 01 65 1c 01 ef 55 72 fe f8 17 4b 67 ac ed 26 72 1f cf aa 24 00 ff ff ff ff 04 54 65 73 74 00
```

Then after alarm went off I turned it on again for tomorrow this is the packet it sent to the device.

```
Value: 0102 0000 0100 C0DA 9169 0009 0101 0106 
0109 0801 651C 01EF 5572 FEF8 174B 67AC 
ED26 721F CFAA 2400 FFFF FFFF 0454 6573 
7401
```

```
Handle Value Notification - Handle:0x0068 - Value: 0100 0200 0300
```

```
Handle Value Notification - Handle:0x0068 - Value: 0402 0003 00
```

this is the new state of the alarm after enabling again:

```
02 00 07 00 2f 00 00 00 00 01 00 c0 da 91 69 00 09 01 01 01 06 01 09 08 01 65 1c 01 ef 55 72 fe f8 17 4b 67 ac ed 26 72 1f cf aa 24 00 ff ff ff ff 04 54 65 73 74 01
```

Seems like flipping on `00` to `01` before `c0` and then sending the same payload along with the ID will enable the alarm again.

Clock time is UTC and user time needs to be converted.

---
How about deleting alarms?

Delete Alarm

```
031E 00
```

`1E 00` is the ID (little endian).

response after delete:

```
0300 1E00
```

```
041E 00FF FF
```

---

How about timers?

Hue also has this feature timers where you can set the light to flash after few minutes.
Fancier way to have a timer than a clock.

```
02 00 38 00 28 00 00 00 00 00 01 b9 ba 94 69 01
01 02 1d 01 50 c1 53 49 69 60 40 b1 b3 38 46 6b
c3 bb 42 58 03 2c 01 00 00 05 54 69 6d 65 72 01
```

Timers have the same format. more or less. The timer name is at the end.

`05 54 69 6d 65 72 01` Timer name.
`b9 ba 94 69` Time that the timer should go off.
`00 01` the Timer is active.
The rest is again mystery bytes.
Before the timer name and before the `00 00` there is `03 2c` that's the timer length in little endian format.


---
TODO: Make this a footnote for more examples of alarm creation.
```
Wake up 07:00 sunrise fade in 30 min

01FF FF00 0100 D8B6 8E69 0009 0101 0106 0109 0801 5B19 0194 D184 84B7 5143 DAA8 67A9 2F02 110C 8D00 FFFF FFFF 0141 01

--
Wake up 06:50 sunrise fade in 20 min

01FF FF00 0100 D8B6 8E69 0009 0101 0106 0109 0801 6519 01CA 492E A08E 6A48 6883 4FC0 1C5B 8E8F 4700 FFFF FFFF 0141 01

--
Wake up 06:50 sunrise fade in 10 min

01FF FF00 0100 30B9 8E69 0009 0101 0106 0109 0801 7D19 01FA 3FD8 C1E2 304D 1E81 948B AE5E C246 3000 FFFF FFFF 0141 01

--
Wake up 07:00 full brightness fade in 30 min

010C 0000 0100 D8B6 8E69 000E 0101 0102 01FE 0302 BF01 0502 5046 1901 2114 F58F E794 40F1 86C4 BF6A 8529 73C4 00FF FFFF FF01 4101

--
Wake up 06:50 full brightness fade in 20 min

01FF FF00 0100 D8B6 8E69 000E 0101 0102 01FE 0302 BF01 0502 E02E 1901 BE74 4F8A 71FA 464D 8C10 910D 7983 676C 00FF FFFF FF01 4101

--
Wake up 06:50 full brightness fade in 10 min

01FF FF00 0100 30B9 8E69 000E 0101 0102 01FE 0302 BF01 0502 7017 1901 AA85 9C87 96F4 4A08 A30D 26A7 E9E0 629B 00FF FFFF FF01 4101

--
Wake up 06:50 sunrise fade in 30 min
01FF FF00 0100 80B4 8E69 0009 0101 0106 0109 0801 5B19 012D A26C 130F A94B F882 E9C3 215C 27A4 8700 FFFF FFFF 0141 01

--
Wake up 06:50 full brightness fade in 30 min
01FF FF00 0100 80B4 8E69 000E 0101 0102 01FE 0302 BF01 0502 5046 1901 1478 FFD5 B1F1 431E AB18 E212 A720 34D6 00FF FFFF FF01 4101
```
