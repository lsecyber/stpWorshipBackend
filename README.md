# stpWorshipBackend

This is a project I created in Python to run a theatre company's lyric and chord chart display system. All of the code is written in Python/Flask.

## Project Background

[Spiritual Twist Productions](https://spiritualtwist.com/) (STP) had a backstage worship setup, but lacked an effective method to manage chord charts and display lyrics. A laptop had to be plugged into the TV on the wall and lyrics were Googled, causing ads to appear on the side. Additionally, due to a poor network connection, they were unable to reliably load chord charts on various iPads and tablets.

## My Solution

I created a custom Vue.Js frontend ([repo link](https://github.com/lsecyber/stp-worship)) and Python backend (this repo) to fix the issues that STP was having. I installed a Raspberry Pi behind the TV in the room, and this broadcasted its own hidden SSID wifi network. I then purchased an Android tablet and a Android phone, and installed a lockdown browser on each so they loaded a specific page (hosted on the Raspberry Pi). This repo provides the server that powers the backend for this system.

## Project Details

This system provides the backend for the frontend that shows the lyrics on one page, shows the chord charts and controls to switch between lyric sections on another page, and shows just the controls for the phone on a 3rd page (so someone who is playing guitar while leading can have someone else control the lyrics/page flipping). The system uses socket.io to communicate between devices to know when to flip pages, change songs, or change lyric sections for display.

## Want to learn more?

If you're interested in me creating a similar setup for your environment, want to learn more about this code, or have a related question, you can reach me at [this link](https://lukeertzberger.com/contact). To view the frontend repo for this project, [click here](https://github.com/lsecyber/stp-worship).
