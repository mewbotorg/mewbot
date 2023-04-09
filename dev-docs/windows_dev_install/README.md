<!--
SPDX-FileCopyrightText: 2023 Mewbot Developers <mewbot@quicksilver.london>

SPDX-License-Identifier: BSD-2-Clause
-->

# Why windows?

The aim of the mewbot project is to allow people to create chatbots with minimal coding experience.
Many of these people will be using a Windows environment.
As such it's vital that mewbot be wel supported on Windows.
Perhaps the only reliable way to do this is to do (some) of the dev on Windows.
If nothing else so the devs can notice and fix problems as they arise.

This guide will
 - walk you through setting up a Windows mewbot dev environment
 - instruct you in how to start contributing to the project
 - hopefully provide some useful troubleshooting tips for if your current dev environment has gone wrong

These instructions are intended for Windows 10 & Windows 11 only.

They should also work on Windows Server and Windows on Arm - but these have not been tested.

## What do I need to do before I start?

 - Ideally, you should be familiar with the basics of `python` programming
 - Likewise `git` - though a full introduction is beyond the scope of these docs
 - Backup your files.
 - Get a cup of tea

### Where can I learn about python?

There are many excellent courses online.

This might not be a bad place to start
 - [Code Academy](https://www.codecademy.com/catalog/language/python)

### Where can I learn about git?

To contribute to mewbot, you don't need to know much git.
`pull`, `push` and `pull reqest` should cover you.

You might want to check out
 - [w3schools basic guide](https://www.w3schools.com/git/git_intro.asp?remote=github)
 - [github desktop basic guide](https://docs.github.com/en/desktop)

### re. Backing up your files.

There is no one, perfect, dev environment.
Everyone is different, with different tastes.
As such, this guide aims to provide options - to allow you to build a dev environment which works will for you.
Some of these options involve registry edits.
Which may, in unlikely circumstances, damage your operating system.
Please do not take these measures unless you are prepared for this possibility.

## How to use these docs

This folder contains a series of numbered files.
Proceeding through them in order should yield a completed environment at the end of it.
Alternatively, if you are an experience dev, you can just read the quickstart guide.

If you run into any problems, we would be most grateful if you would append a summary of what went wrong and how you fixed it to the troubleshooting.md doc in this folder.

## FAQ

### Where can I get help?

We will be delighted to help in any way we can.

Please start by posting your issue to our github issue tracker, [which you can find here](https://github.com/mewler/mewbot/issues).

**DISCLAIMER**

We do not assume any responsibility for damage caused to your operating system, place of business, or other property from following these instructions.
Proceed at your own risk.

In full (taken from [the three clause BSD license](https://opensource.org/license/bsd-3-clause/))

THIS SOFTWARE AND DOCUMENTATION IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, 
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, 
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
HETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF 
THIS SOFTWARE, INCLUDING ANY DOCUMENTATION, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
