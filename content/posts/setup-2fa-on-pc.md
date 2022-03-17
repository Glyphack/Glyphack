---
title: "How to Setup 2 Factor Authentication Code Generator on PC"
date: 2022-03-17T23:19:14+03:30
draft: true
tags: [tools] 
---

I use 2 factor authentication with almost all of my accounts, the only downside of this is that when I need to access something frequently or automate some task I have to manually enter this code from my phone.

So I searched a bit and found these tools to make this process easier, I imported 2fa keys to my laptop and can generate keys with a command so I can copy the code and also the command can be used in automated tasks. Note that in this way anyone with access to your laptop has access to 2fa codes too.

## Setup 2FA code on your machine

Here's the process:

### 1. Export 2FA Accounts From Google Authenticator

You probably have already setup your accounts with google authenticator. You can use the [export option](https://support.google.com/accounts/thread/107807857/how-to-export-2fa-codes-from-google-authenticator?hl=en) to export the accounts you need. Export will be a qr code so you need a way to convert it to text. On mac I did it with [qr journal](https://apps.apple.com/us/app/qr-journal/id483820530?mt=12) .

```bash
brew install --cask qr-journal
```

### 2. Extract Account Secret Key

Once you have the qr code as text you can use [extract_otp_secret_keys](https://github.com/scito/extract_otp_secret_keys) to read the text and get the secret strings. save exported qr code in a text file and read it with like this:

```bash
gh repo clone scito/extract_otp_secret_keys
python extract_otp_secret_keys/extract_otp_secret_keys.py -p exported.txt
```

This will output the final secret key for accounts.

### 3. Install a 2FA Code Generator

I used the [2fa](https://github.com/rsc/2fa) app to import accounts in terminal.

```bash
go install rsc.io/2fa@latest
2fa -add account_name
```

Now that you have this you can use the command `2fa` to get all of your accounts 2FA codes or `2fa account_name` to get the 2FA code for a specific account, the latter is useful when writing scripts.
