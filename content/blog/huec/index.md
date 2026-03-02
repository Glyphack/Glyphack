---
title: "Reverse Engineering Philips Hue light strip to control from pc"
date: 2026-02-25T22:25:08+01:00
draft: true
tags: [] 
---

I was looking for a way to control my Philips light without their terrible app[^1].
All my searches led to this conclusion: you need to buy a hue bridge to control the lamp from pc.
But I don't want to have another device just to do what my pc is capable of doing right now.

I want my light to turn on and off automatically every day without paying for another device. I also want to control it from my desk without grabbing my phone.

I published the end result of this project in [huec](https://github.com/Glyphack/hue-control), a CLI app that lets you control Philips lights.
Here I discuss the journey of discovering the protocol, explaining how power, brightness, color, and alarms are controlled.

## Usages

Here are some usage scenarios I have for `huec`

**Turn lights on and off everyday**

I have two alarms for my light to turn on at 07:00 and turn off at 08:00.
To have this repeat everyday I run the following command:
```text
huec alarms enable --all
```

I have a 5 minute timer on the light.
Using this script I can trigger this timer to start.

```py
result = run("uv run huec alarms list --json")
alarms = json.loads(result.stdout)
matches = [a for a in alarms if a["name"] == "Timer"]
if not matches:
    print("No alarm named 'Timer' found", file=sys.stderr)
    sys.exit(1)

alarm_id = matches[0]["id"]
print(f"Enabling alarm ID: {alarm_id}")
run(f"uv run huec alarms enable --id {alarm_id}")
```

Without further ado, let’s see what I figured out to control the light!

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
- [Bluetooth logging config for iOS](https://developer.apple.com/services-account/download?path=/iOS/iOS_Logs/iOSBluetoothLogging.mobileconfig)[^2]

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

When the app connects it writes this to the characteristic:

{{< ble-packet payload="00" >}}
0 | Command | Request alarm list
{{< /ble-packet >}}

Then the characteristic responds back with the list of alarm IDs:

{{< ble-packet payload="00 00 07 02 2C 00 2D 00" >}}
0-2 | Constant | Response type (alarm list)
3   | Count   | Number of alarms (2)
4-5 | Alarm 1 ID | Little-endian 16-bit ID (0x002C = 44)
6-7 | Alarm 2 ID | Little-endian 16-bit ID (0x002D = 45)
{{< /ble-packet >}}

To read the alarm details using its ID. We construct this message:

{{< ble-packet payload="02 2C 00 00 00" >}}
0   | Command  | Read alarm details
1-2 | Alarm ID | Little-endian 16-bit ID (0x002C = 44)
3-4 | Padding  |
{{< /ble-packet >}}

Which gives us the full alarm details:

{{< ble-packet payload="02 00 2C 00 35 00 00 00 00 01 00 60 55 95 69 00 09 01 01 01 06 01 09 08 01 7D 22 01 D4 0C 13 8D 81 B9 4A 4C AA 42 B9 9A CE C6 2D 88 00 FF FF FF FF 0A 4D 6F 72 6E 69 6E 67 20 75 70 01" >}}
0-1   | Command    | Response type (alarm info)
2-3   | Alarm ID   | Little-endian 16-bit ID (0x002C = 44)
4     | Length     | Payload length (0x35 = 53 bytes)
5-8   | Padding    |
9-10  | Active     | Alarm state (01 00 = active)
11-14 | Timestamp  | Little-endian Unix timestamp (2026-02-16 6:00 UTC)
15-44 | Mystery    | Unknown bytes, possibly effect and crypto data
45-48 | Separator  | Always FF FF FF FF, lamp ignores this value
49-60 | Name       | Length-prefixed alarm name "Morning up" + 01 terminator
{{< /ble-packet >}}

That's it. You can read and parse the alarm.

Can we create any alarm we like now?
No, I tried this, the problem is that the magic bytes seem to have a special meaning.
When I took this same message and just tried to create random alarms by substituting my timestamp and name the lamp was not creating the alarm.

From my investigation I found this is the packet that the app uses to create an alarm.

{{< ble-packet payload="01 FF FF 00 01 00 D8 B6 8E 69 00 09 01 01 01 06 01 09 08 01 5B 19 01 94 D1 84 84 B7 51 43 DA A8 67 A9 2F 02 11 0C 8D 00 FF FF FF FF 01 41 01" >}}
0-1   | Command   | 01 FF to create a new alarm
2-3   | State     | 01 00 tells the alarm is active
4-7   | Timestamp | Little-endian Unix timestamp
8-19  | Effect    | Sunrise effect
20-39 | Mystery   | Unknown bytes, possibly crypto data
40-43 | Separator | Always FF FF FF FF
44-46 | Name      | Length-prefixed alarm name + 01 terminator
{{< /ble-packet >}}

After alarm write is success there will be these two notifications which reply with the ID of the alarm.
It's useful to verify the write actually happened. But I didn't get any extra information from it.

{{< ble-packet payload="01 00 FF FF 1E 00" >}}
0     | Command  | 01 echoes back the create command
1     | Status   | 00 indicates success
2-3   | Separator| FF FF
4-5   | Alarm ID | Little-endian 16-bit ID of the created alarm (0x001E = 30)
{{< /ble-packet >}}

{{< ble-packet payload="04 FF FF 1E 00" >}}
0     | Command  | 04 confirmation notification
1-2   | Separator| FF FF
3-4   | Alarm ID | Little-endian 16-bit ID matching the created alarm (0x001E = 30)
{{< /ble-packet >}}

With this information I was hoping that I can create any alarm I want.
But when I created an alarm it would not be created.
So then I checked what happens when I create the same alarm twice via the app.

First alarm creation payload:

{{< ble-packet payload="01 FF FF 00 01 00 30 5C 91 69 00 09 01 01 01 06 01 09 08 01 65 1F 01 FB D0 61 C2 5B 63 40 F6 AA 71 BB 49 E1 86 F0 C9 00 FF FF FF FF 07 57 61 6B 65 20 75 70 01" >}}
0-22  | Alarm time | Command, state, timestamp, and effect — identical in both
23-39 | Mystery    | FB D0 61 C2 5B 63 40 F6 AA 71 BB 49 E1 86 F0 C9 00
40-52 | Name       | Separator + name "Wake up" — identical in both
{{< /ble-packet >}}

Second alarm creation, same configuration:

{{< ble-packet payload="01 FF FF 00 01 00 30 5C 91 69 00 09 01 01 01 06 01 09 08 01 65 1F 01 85 97 FE 88 1C C1 46 47 A1 9D 9F 6A 8C 2C 29 7B 00 FF FF FF FF 07 57 61 6B 65 20 75 70 01" >}}
0-22  | Alarm time | Command, state, timestamp, and effect — identical in both
23-39 | Mystery    | 85 97 FE 88 1C C1 46 47 A1 9D 9F 6A 8C 2C 29 7B 00 — only these bytes changed
40-52 | Name       | Separator + name "Wake up" — identical in both
{{< /ble-packet >}}

As you see the bytes in the middle change.
We don't have any change in the alarm configuration.
This suggests that the app generates these bytes as a checksum.
The lamp checks the checksum to verify if the alarm is valid or not.
Which means if I just use repeat this with any configuration I want it's not going to work.

After spending some time on it[^3] I decided to come up with another solution to control alarms.
My goal was to have an alarm that repeats every day.
What if I can just change the activate byte of the alarm and it would be enabled every day? 

Then I created and alarm and turned it off and on again in the app.
I already knew how to read alarm information.
I was able to read the alarm info and see what has changed.

Create a new alarm called "Test":

{{< ble-packet payload="01 FF FF 00 01 00 40 89 90 69 00 09 01 01 01 06 01 09 08 01 65 1C 01 EF 55 72 FE F8 17 4B 67 AC ED 26 72 1F CF AA 24 00 FF FF FF FF 04 54 65 73 74 01" >}}
0-1   | Command   | 01 FF to create a new alarm
2-3   | State     | 00 01 00 tells the alarm is active
4-7   | Timestamp | Little-endian Unix timestamp
8-19  | Effect    | Sunrise effect
20-39 | Mystery   | Unknown bytes, possibly crypto data
40-43 | Separator | Always FF FF FF FF
44-49 | Name      | Length-prefixed alarm name "Test" + 01 terminator
{{< /ble-packet >}}

Response confirming the alarm was created with ID 1:

{{< ble-packet payload="01 00 FF FF 01 00" >}}
0     | Command  | 01 echoes back the create command
1     | Status   | 00 indicates success
2-3   | Separator| FF FF
4-5   | Alarm ID | Little-endian 16-bit ID (0x0001 = 1)
{{< /ble-packet >}}

{{< ble-packet payload="04 FF FF 01 00" >}}
0     | Command  | 04 confirmation notification
1-2   | Separator| FF FF
3-4   | Alarm ID | Little-endian 16-bit ID matching the created alarm (0x0001 = 1)
{{< /ble-packet >}}

After the alarm went off I read the alarm details. Alarm active byte is 0:

{{< ble-packet payload="02 00 06 00 2F 00 00 00 00 00 00 C0 DA 91 69 00 09 01 01 01 06 01 09 08 01 65 1C 01 EF 55 72 FE F8 17 4B 67 AC ED 26 72 1F CF AA 24 00 FF FF FF FF 04 54 65 73 74 01" >}}
0-1   | Command    | Response type (alarm info)
2-3   | Alarm ID   | Little-endian 16-bit ID (0x0006)
4     | Length     | Payload length (0x2F = 47 bytes)
5-8   | Padding    |
9-10  | Active     | Alarm state (00 00 = inactive, alarm has fired)
11-14 | Timestamp  | Little-endian Unix timestamp
15-44 | Mystery    | Unknown bytes, possibly effect and crypto data
45-48 | Separator  | Always FF FF FF FF
49-54 | Name       | Length-prefixed alarm name "Test" + 00 terminator (inactive)
{{< /ble-packet >}}

Then I turned it on again for tomorrow via the app. This is the edit request sets the active byte to 1:

{{< ble-packet payload="01 02 00 00 01 00 C0 DA 91 69 00 09 01 01 01 06 01 09 08 01 65 1C 01 EF 55 72 FE F8 17 4B 67 AC ED 26 72 1F CF AA 24 00 FF FF FF FF 04 54 65 73 74 01" >}}
0     | Command   | 01 to edit an existing alarm
1-2   | Alarm ID  | Little-endian 16-bit ID (0x0002)
3-4   | State     | 00 01 00 tells the alarm is active
5-8   | Timestamp | Little-endian Unix timestamp
9-20  | Effect    | Sunrise effect
21-40 | Mystery   | Same crypto data as the original alarm
41-44 | Separator | Always FF FF FF FF
45-49 | Name      | Length-prefixed alarm name "Test" + 01 terminator
{{< /ble-packet >}}

Responses confirming the edit:

{{< ble-packet payload="01 00 02 00 03 00" >}}
0     | Command  | 01 echoes back the edit command
1     | Status   | 00 indicates success
2-3   | Alarm ID | Little-endian 16-bit ID (0x0002)
4-5   | Version  | Little-endian revision counter (0x0003 = 3)
{{< /ble-packet >}}

{{< ble-packet payload="04 02 00 03 00" >}}
0     | Command  | 04 confirmation notification
1-2   | Alarm ID | Little-endian 16-bit ID (0x0002)
3-4   | Version  | Little-endian revision counter (0x0003 = 3)
{{< /ble-packet >}}

Reading the alarm again after re-enabling byte 9 is now `01` (active):

{{< ble-packet payload="02 00 07 00 2F 00 00 00 00 01 00 C0 DA 91 69 00 09 01 01 01 06 01 09 08 01 65 1C 01 EF 55 72 FE F8 17 4B 67 AC ED 26 72 1F CF AA 24 00 FF FF FF FF 04 54 65 73 74 01" >}}
0-1   | Command    | Response type (alarm info)
2-3   | Alarm ID   | Little-endian 16-bit ID (0x0007)
4     | Length     | Payload length (0x2F = 47 bytes)
5-8   | Padding    |
9-10  | Active     | Alarm state (01 00 = active)
11-14 | Timestamp  | Little-endian Unix timestamp
15-44 | Mystery    | Unknown bytes, possibly effect and crypto data
45-48 | Separator  | Always FF FF FF FF
49-54 | Name       | Length-prefixed alarm name "Test" + 01 terminator (active)
{{< /ble-packet >}}

So in order to turn on the alarm for the next day I have to do two things:

- change activate byte to `01`.
- Update the time stamp to be the next day. The alarm time stamp contains date and time. Clock time is UTC and user time needs to be converted.

### Timers

Philips app also has a feature called timer.
You can start a timer and after it reaches 0 the light starts flashing.

{{< ble-packet payload="02 00 38 00 28 00 00 00 00 00 01 b9 ba 94 69 01 01 02 1d 01 50 c1 53 49 69 60 40 b1 b3 38 46 6b c3 bb 42 58 03 2c 01 00 00 05 54 69 6d 65 72 01" >}}
0-1   | Command    | alarm info
2-3   | Alarm ID   | Little-endian 16-bit
4     | Payload length     |
5-8   | Padding    |
9-10  | Active     | Alarm state (01 00 = active)
11-14 | Timestamp  | Little-endian Unix timestamp
15-36 | Mystery    |
37-38 | Timer length  | little endian number
39-40 | Separator       | 
41-47 | Name       | Length-prefixed alarm name "Test" + 01 terminator (active)
{{< /ble-packet >}}

Timers can be turned on and off in the same way.
So the code that turns alarms on and off works on timers too.

### Deleting Alarms

Deleting alarms happen using the same characteristic.

By setting first byte to `03` we can make a delete alarm request. For example:

Delete alarm with ID 30:

{{< ble-packet payload="03 1E 00" >}}
0     | Command  | 03 to delete an alarm
1-2   | Alarm ID | Little-endian 16-bit ID (0x001E = 30)
{{< /ble-packet >}}

Response confirming the deletion:

{{< ble-packet payload="03 00 1E 00" >}}
0     | Command  | 03 echoes back the delete command
1     | Status   | 00 indicates success
2-3   | Alarm ID | Little-endian 16-bit ID (0x001E = 30)
{{< /ble-packet >}}

{{< ble-packet payload="04 1E 00 FF FF" >}}
0     | Command  | 04 confirmation notification
1-2   | Alarm ID | Little-endian 16-bit ID (0x001E = 30)
3-4   | Separator| FF FF
{{< /ble-packet >}}

---

[^1]: I have a lot to say about Philips, not only they cannot make one app to control all the stuff you have from Philips in your home. Their individual apps suck. They are slow. There is startup time. They don't have good features. I guess you need to buy Hue from them to have this basic functionality? But I don't want to spend more money on Philips.

[^2]: You need an Apple account to download it. I hate this because when I was in Iran many of these tools were blocked because you can't easily open an account. I have since moved to a place where I am allowed to open an account, so I have it.

[^3]: I created more alarms with different configurations trying to figure out the mystery bytes but I did not find a pattern. Let me know if you do!
    <details>
    <summary>alarm creation packets</summary>

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
