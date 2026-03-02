---
title: "Reverse Engineering Philips Hue light strip to control from pc"
date: 2026-02-25T22:25:08+01:00
draft: true
tags: [] 
---

I was looking for a way to control my Philips light without their terrible app.
All my searches led to this conclusion: you need to buy a hue bridge to control the lamp from pc.
But I don't want to have another device just to do what my pc is capable of doing right now.

I want my light to turn on and off automatically every day without paying for another device. I also want to control it from my desk without grabbing my phone.

I published the end result of this project in [huec](https://github.com/Glyphack/hue-control), a CLI app that lets you control Philips lights.
Here I discuss the journey of discovering the protocol, explaining how power, brightness, color, and alarms are controlled.

<!-- End of introduction -->

It all started when I found [Blendr](https://github.com/dmtrKovalenko/blendr/).
Blendr connects to Bluetooth Low Energy (BLE) devices and lets you browse their services and characteristics.

Characteristics are a place where light stores some data.
You can get data from a characteristic or write into it.
A service is simply a group of characteristic.
For example a service could be for changing color and brightness.

Here's how the output looked like for my lamp:

```text
Service Device Information (0x1800)
  Manufacturer Name String (0x2A29) [Read]
  Model Number String (0x2A24) [Read]
  Software Revision String (0x2A28) [Read]

Service 932c32bd-0001-47a2-835a-a8d455b859dd
  932c32bd-0001-47a2-835a-a8d455b859dd [Read]
  932c32bd-0002-47a2-835a-a8d455b859dd [Read, Write, Notify]
  932c32bd-0003-47a2-835a-a8d455b859dd [Read, Write, Notify]
  932c32bd-0004-47a2-835a-a8d455b859dd [Read, Write, Notify]
  932c32bd-0005-47a2-835a-a8d455b859dd [Read, Write, Notify]   — RGB Color
  932c32bd-0006-47a2-835a-a8d455b859dd [Write]
  932c32bd-0007-47a2-835a-a8d455b859dd [Read, Write, Notify]
  932c32bd-1005-47a2-835a-a8d455b859dd [Read, Write]

Service 97fe6561-0001-4f62-86e9-b71ee2da3d22
  97fe6561-0001-4f62-86e9-b71ee2da3d22 [Read]
  97fe6561-0003-4f62-86e9-b71ee2da3d22 [Read, Write]
  97fe6561-0004-4f62-86e9-b71ee2da3d22 [Write]
  97fe6561-0005-4f62-86e9-b71ee2da3d22 [Write]
  97fe6561-0006-4f62-86e9-b71ee2da3d22 [Read, Write]
  97fe6561-0008-4f62-86e9-b71ee2da3d22 [Write, Notify]
  97fe6561-1001-4f62-86e9-b71ee2da3d22 [Read, Write, Notify]
  97fe6561-2001-4f62-86e9-b71ee2da3d22 [Read, Write]
  97fe6561-2002-4f62-86e9-b71ee2da3d22 [Write]
  97fe6561-2004-4f62-86e9-b71ee2da3d22 [Write]
  97fe6561-a001-4f62-86e9-b71ee2da3d22 [Write]
  97fe6561-a002-4f62-86e9-b71ee2da3d22 [Read]
  97fe6561-a003-4f62-86e9-b71ee2da3d22 [Read, Write]

Service 9da2ddf1-0001-44d0-909c-3f3d3cb34a7b
  9da2ddf1-0001-44d0-909c-3f3d3cb34a7b [Write, Notify]

Service b8843add-0001-4aa1-8794-c3f462030bda
  b8843add-0001-4aa1-8794-c3f462030bda [Read]
  b8843add-0002-4aa1-8794-c3f462030bda [Write, Notify]
  b8843add-0003-4aa1-8794-c3f462030bda [Write]
  b8843add-0004-4aa1-8794-c3f462030bda [Read]
```

Some characteristics have "Read" in front of them.
This means you can read their values, using Blendr.

Now the question is, what does each characteristic do?
There are two ways to find this out:

Randomly write data into different characteristics to see if the lamp reacts
For example we can write `0x0` into all characteristics and see when the lamp turns off.
This requires guessing the value for example what turns the light on and off and what value changes the color.

Use the app to change properties of the lamp and then read values using Blendr.
I turned the lamp off and checked what characteristic has `0x0` in it.
It was the `932c32bd-0002-47a2-835a-a8d455b859dd`.
Which suggests that it's for the power.

To send and receive data from the lamp there is [Bleak](https://bleak.readthedocs.io/en/latest/).

By knowing the name of the lamp(you can get it from Blendr) you can connect to the lamp using:

```py
POWER_UUID = '932c32bd-0002-47a2-835a-a8d455b859dd'

async def connect_to_light(name: str, timeout: float = 10.0) -> BleakClient:
    device = await BleakScanner.find_device_by_name(name, timeout=timeout)
    if not device:
        raise SystemExit(f"Device '{name}' not found.")

    client = BleakClient(device, timeout=timeout)
    await client.connect(timeout=timeout)
    return client

await client.write_gatt_char(POWER_UUID, b"\x01")  # turn on
await client.write_gatt_char(POWER_UUID, b"\x00")  # turn off
```

The `client` then can be used to read and write values.

## Color

I looked around in the characteristics and tried out all the characteristics below the on/off one.

You can easily find out the pattern by changing the light color and observing the characteristic values.
There are multiple characteristics that change when you change the light color:

- `932c32bd-0003-47a2-835a-a8d455b859dd` changes with brightness
- `932c32bd-0005-47a2-835a-a8d455b859dd` changes with color (if I do warm white then cool white stays the same)
- `932c32bd-0007-47a2-835a-a8d455b859dd` changes with everything.

The third option is more general hence more useful.
The value inside of it looks like this:

Cool white:

{{< ble-packet payload="01 01 01 02 01 FE 03 02 9C 00" >}}
0-4 | Constant |
5   | Brightness |
6-7  | Mode | 03 02 for white 04 04 for colors
8-9 | Color temperature | Little-endian 16-bit value in mireds
{{< /ble-packet >}}

Warm white:

{{< ble-packet payload="01 01 01 02 01 FE 03 02 5A 01" >}}
0-4 | Constant |
5   | Brightness |
6-7 | Mode | 03 02 for white
8-9 | Color temperature | Little-endian 16-bit value in mireds
{{< /ble-packet >}}

The temperature values are in [mireds](https://en.wikipedia.org/wiki/Mired), which is how Philips Hue encodes color temperature.
Warm white and cool white only differ in bytes 8-9.

When I set it to another color the bytes change to this format:

For example, here's the packet for red

{{< ble-packet payload="01 01 01 02 01 fe 04 04 c5 af 51 4e" >}}
0-4 | Constant |
5   | Brightness |
6-7 | Mode | 04 04 for colors
8-9 | X value | Little-endian 16-bit value for X
10-11 | Y value | Little-endian 16-bit value for Y
{{< /ble-packet >}}

The color is encoded in [CIE xy](https://en.wikipedia.org/wiki/CIE_1931_color_space) format.

Philips hue [developer docs](https://developers.meethue.com/develop/application-design-guidance/color-conversion-formulas-rgb-to-xy-and-back/#xy-to-rgb-color) require login! So I asked AI to figure out what's this format and how can I get to it from RGB.

1. Convert the 8 bit number from R/G/B into a number between 0 and 1
2. Linearise the numbers based on this forumla `if g > 0.04045 then g / 12.92 else ((g + 0.055) / 1.055) ^ 2.4`
3. Apply matrix transformation, one full matrix example is [here](https://www.image-engineering.de/library/technotes/958-how-to-convert-between-srgb-and-ciexyz).

You can play around with it in the box below:

{{< hue/xy-convertor >}}

Now that we know the payload format we can use this code to send the packet to lamp:


When you run the app in interactive mode with `huec interactive` it will open up a browser page and runs a server.
The browser displays a color picker and calculates the payload for the color based on explanations above.
The server accepts the payload and sends it to the light using Bleak.

```py
async def set_color(self, data: bytes) -> None:
    COLOR_UUID = "932c32bd-0007-47a2-835a-a8d455b859dd"
    await self.client.write_gatt_char(COLOR_UUID, data, response=True)
```
## Alarms

Timer in Philips app is a functionality to turn on/off the light at specific time or create countdown to flash the lights.

But there are some limitations for example when you set the alarm to turn on in the morning it will only turn on the next day.
If I want it to turn on the day after I need to again toggle the alarm for the next day. (I like to rewrite this with simpler words in once sentence.)

Similar to how I discovered how colors work I tried to look into what characteristics change when I create an alarm.
But I didn't see anything changing.

I needed to see what my phone was doing to create alarms.

For capturing Bluetooth packets there are tools like Wireshark.
These tools allow you to see what data software running on the system is sending to where.
I was using MacOS + iOS. For this combination there is:

- [Bluetooth Packet Logger](https://developer.apple.com/bluetooth/)
- [Bluetooth logging config for iOS](https://developer.apple.com/services-account/download?path=/iOS/iOS_Logs/iOSBluetoothLogging.mobileconfig) (add footnote apple id and sanctions, text is at the end)

Install Packet Logger on your computer and the profile on your iPhone. 
Then, connect the phone to the computer.
Start using the app, and you will see the packets being sent or received.

After setting up the tools I checked what is happening when the app connects to the light.
The logs looked like this:

```text
0x005A  Hue lightstrip pl  Write Request - Handle:0x0068 - Value: 0311 00  
	Write Request - Handle:0x0068 - Value: 0311 00
	Opcode: 0x12
	Attribute Handle: 0x0068 (104)
	Value: 0311 00
0x005A  Hue lightstrip pl  Channel ID: 0x0004  Length: 0x0006 (06) [ 12 68 00 03 11 00 ]  
	Channel ID: 0x0004  Length: 0x0006 (06) [ 12 68 00 03 11 00 ]
	L2CAP Payload:
	00000000: 1268 0003 1100                           .h....
0x005A  Hue lightstrip pl  Data [Handle: 0x005A, Packet Boundary Flags: 0x0, Length: 0x000A (10)]  
0x005A  Hue lightstrip pl  Write Response  
	Write Response
	Opcode: 0x13
0x005A  Hue lightstrip pl  Channel ID: 0x0004  Length: 0x0001 (01) [ 13 ]  
	Channel ID: 0x0004  Length: 0x0001 (01) [ 13 ]
	L2CAP Payload:
	00000000: 13                                       .
0x005A  Hue lightstrip pl  Data [Handle: 0x005A, Packet Boundary Flags: 0x2, Length: 0x0005 (5)]  
0x005A  Hue lightstrip pl  Handle Value Notification - Handle:0x0068 - Value: 0300 1100  
	Handle Value Notification - Handle:0x0068 - Value: 0300 1100
	Opcode: 0x1B
	Attribute Handle: 0x0068 (104)
0x005A  Hue lightstrip pl  Channel ID: 0x0004  Length: 0x0007 (07) [ 1B 68 00 03 00 11 00 ]  
	Channel ID: 0x0004  Length: 0x0007 (07) [ 1B 68 00 03 00 11 00 ]
	L2CAP Payload:
	00000000: 1B68 0003 0011 00                        .h.....
0x005A  Hue lightstrip pl  Data [Handle: 0x005A, Packet Boundary Flags: 0x2, Length: 0x000B (11)]  
0x005A  Hue lightstrip pl  Handle Value Notification - Handle:0x0068 - Value: 0411 00FF FF  
	Handle Value Notification - Handle:0x0068 - Value: 0411 00FF FF
	Opcode: 0x1B
	Attribute Handle: 0x0068 (104)
0x005A  Hue lightstrip pl  Channel ID: 0x0004  Length: 0x0008 (08) [ 1B 68 00 04 11 00 FF FF ]  
	Channel ID: 0x0004  Length: 0x0008 (08) [ 1B 68 00 04 11 00 FF FF ]
	L2CAP Payload:
	00000000: 1B68 0004 1100 FFFF                      .h......
0x005A  Hue lightstrip pl  Data [Handle: 0x005A, Packet Boundary Flags: 0x2, Length: 0x000C (12)]  
	Packet Boundary Flags: [10] 0x02 - First Flushable Packet Of Higher Layer Message (Start Of An L2CAP Packet)
	Broadcast Flags: [00] 0x00 - Point-to-point
	Data (0x000C Bytes)
0x0000  00:00:00:00:00:00  00000000: 5A20 0C00 0800 0400 1B68 0004 1100 FFFF  Z .......h......  
0x005A  Hue lightstrip pl  Number Of Completed Packets - Handle: 0x005A - Packets: 0x0001    
	Parameter Length: 5 (0x05)
	Number Of Handles: 0x01
	Connection Handle: 0x005A
	Number Of Packets: 0x0001
```

I asked AI to figure out what the light was doing and gave it the context about what I was looking for.
It figured out that when the app it performs this process:

1. Write `00` to a characteristic.
2. The characteristic replies with current alarm IDs.
3. the app writes each alarm ID to the characteristic again and receives more information about that alarm.

So I learned that characteristics can also reply back.
This happens through subscriptions.
From the first list of characteristics you can see some have read and write properties.
Some characteristics have write and notify properties.
You can write into these characteristics and receive a response back.

Here's the code to do this:

```py
TIMER_UUID = "9da2ddf1-0001-44d0-909c-3f3d3cb34a7b"

notifications = asyncio.Queue()

def on_timer_notification(sender, data: bytearray):
    notifications.put_nowait(data)

await client.start_notify(TIMER_UUID, on_timer_notification)

await client.write_gatt_char(TIMER_UUID, bytes([0x00]))

response = await asyncio.wait_for(notifications.get(), timeout=5.0)
```

You might notice that in the Packet Logger logs there is only a handle. There is no characteristic ID.
I tried a simple approach: I subscribed to all characteristics and then wrote `00` payload to all and checked which one replied back.
That's how I got the characteristic.

Here's the breakdown. The timer characteristic (`9da2ddf1-0001-44d0-909c-3f3d3cb34a7b`) is like a server.
You can write different messages to it and subscribe to it to get back responses as notifications.
When the app connects the first packet is:
```text
0x00
```

Then the application responds back the list of IDs for the alarms that are already set:
```text
00 00 00 03 | ID0_lo ID0_hi | ID1_lo ID1_hi | ID2_lo ID2_hi
```

The `03` is the number of alarms.

So it's basically like a CRUD app.
Next is to read the alarm details using its ID.

We construct this message:
```text
0x02, lo, hi, 0x00, 0x00
```

Which gives us the full alarm details.

Now we have a bit of decoding to do here.
The way I did this was by setting up a lot of alarms and seeing how they change the payload.
In the end I didn't fully decode what this payload means. For me the goal was to enable an alarm every day.
That's what I did.

Let's look at one example:

```text
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
5. `60 55 95 69` is the timestamp for the alarm in little-endian format which is 2026-02-16 6:00.
6. Then you have a series of bytes that I don't know what they are related to, we call them mystery bytes.
7. Then you have `ff ff ff ff` which I think is a separator for the alarm info and the name. I verified it by sending `00 00 00 00` instead and seems like the lamp ignores it.
8. Then you have the name `0a 4d 6f 72 6e 69 6e 67 20 75 70 01` length + characters + `01`

That's it. You can read and parse the alarm.

Can we create any alarm we like now?
No, I tried this, the problem is that the magic bytes seem to have a special meaning.
When I took this same message and just tried to create random alarms by substituting my timestamp and name the lamp was not creating the alarm.

From my investigation I found this is the packet that the app uses to create an alarm.

```text
01FF FF00 0100 D8B6 8E69 0009 0101 0106 0109 0801 5B19 0194 D184 84B7 5143 DAA8 67A9 2F02 110C 8D00 FFFF FFFF 0141 01
```

1. `01FF` is the command to create a new alarm.
2. `0100` tells the alarm is active.
3. `D8B6 8E69` is timestamp in little-endian format.
4. `0009 0101 0106 0109 0801` hasn't changed I guess it's related to the effect (here it's "sunrise").
5.  `5B19 0194 D184 84B7 5143 DAA8 67A9 2F02 110C 8D00` mystery bytes.
6. After `0141 01` separator it's name of the alarm.

After alarm write is success there will be these two notifications which reply with the ID of the alarm.
It's useful to verify the write actually happened. But I didn't get any extra information from it.

```text
0100 FFFF 1E00
```

```text
04FF FF1E 00
```

Then I tried making the same alarm twice with everything and here's the result:

```text
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

Here are the packets for that.
What I did here was turning the alarm on and off and check the alarm by querying the alarm detail the way I explained above with the timer characteristic.

```text
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

```text
Value: 01FF FF00 0100 4089 9069 0009 0101 0106 
0109 0801 651C 01EF 5572 FEF8 174B 67AC 
ED26 721F CFAA 2400 FFFF FFFF 0454 6573 
7401
```

```text
Handle Value Notification - Handle:0x0068 -Value: 0100 FFFF 0100
```

```text
Handle Value Notification - Handle:0x0068 - Value: 04FF FF01 00
```

After alarm went off this is the alarm payload using read alarms:

```text
02 00 06 00 2f 00 00 00 00 00 00 c0 da 91 69 00 09 01 01 01 06 01 09 08 01 65 1c 01 ef 55 72 fe f8 17 4b 67 ac ed 26 72 1f cf aa 24 00 ff ff ff ff 04 54 65 73 74 00
```

Then after alarm went off I turned it on again for tomorrow this is the packet it sent to the device.

```text
Value: 0102 0000 0100 C0DA 9169 0009 0101 0106 
0109 0801 651C 01EF 5572 FEF8 174B 67AC 
ED26 721F CFAA 2400 FFFF FFFF 0454 6573 
7401
```

```text
Handle Value Notification - Handle:0x0068 - Value: 0100 0200 0300
```

```text
Handle Value Notification - Handle:0x0068 - Value: 0402 0003 00
```

This is the new state of the alarm after enabling again:

```text
02 00 07 00 2f 00 00 00 00 01 00 c0 da 91 69 00 09 01 01 01 06 01 09 08 01 65 1c 01 ef 55 72 fe f8 17 4b 67 ac ed 26 72 1f cf aa 24 00 ff ff ff ff 04 54 65 73 74 01
```

Seems like flipping on `00` to `01` before `c0` and then sending the same payload along with the ID will enable the alarm again.

Clock time is UTC and user time needs to be converted.

---
How about deleting alarms?

Delete Alarm

```text
031E 00
```

`1E 00` is the ID (little-endian).

Response after delete:

```text
0300 1E00
```

```text
041E 00FF FF
```

---

How about timers?

Hue also has this feature timers where you can set the light to flash after few minutes.
Fancier way to have a timer than a clock.

```text
02 00 38 00 28 00 00 00 00 00 01 b9 ba 94 69 01
01 02 1d 01 50 c1 53 49 69 60 40 b1 b3 38 46 6b
c3 bb 42 58 03 2c 01 00 00 05 54 69 6d 65 72 01
```

Timers have the same format. More or less. The timer name is at the end.

`05 54 69 6d 65 72 01` Timer name.
`b9 ba 94 69` Time that the timer should go off.
`00 01` the Timer is active.
The rest is again mystery bytes.
Before the timer name and before the `00 00` there is `03 2c` that's the timer length in little-endian format.


---
These should be footnotes
<details>
<summary>More examples of alarm creation packets</summary>

```text
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

</details>

(I have a lot to say about Philips, not only they cannot make one app to control all the stuff you have from Philips in your home. Their individual apps suck. They are slow. There is startup time. They don't have good features. I guess you need to buy Hue from them to have this basic functionality? But I don't want to spend more money on Philips.)

You need an Apple account to download it.
I hate this because when I was in Iran many of these tools were blocked because you can't easily open an account.
I have since moved to a place where I am allowed to open an account, so I have it.
