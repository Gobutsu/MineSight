# 🔍 MineSight - Investigate a minecraft account
<p align="center">
    <img src="https://files.catbox.moe/0kx02e.png" height="100">
</p>

## 🤔 What is it?
Enter a minecraft username or UUID and get a list of servers the account has been on.
You can obtain this kind of information:
- When the account was last seen
- What are his old usernames
- Any other fields that the servers websites publicly display (language, social media, etc)

## 📦 Installation
You can either install it from Github (recommended):
```
git clone https://github.com/Gobutsu/MineSight
cd MineSight
python setup.py install
```
Or from Pypi:
```
pipx install minesight
```
Installation can be confirmed by typing `minesight` in a terminal.

## 🚀 How to use it?
```
minesight [-u USERNAME] [-i UUID]
```

## ☁️ Inspiration
This tool works in a quite similar way to [Maigret](https://github.com/soxoj/maigret).
I wanted to make a tool that would work with minecraft accounts, and I thought that Maigret's way of working was perfect for this.
MineSight is basically a Maigret for minecraft accounts. And the fun thing is, players often have no idea that servers publicly display their information, so they don't bother to hide it.

## 🕵️ Disclaimer
This tool is meant to be used for educational purposes only. I am not responsible for any misuse of this tool. Use it legally and ethically.