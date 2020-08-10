# Simple photo processing automation

This automates basic processing of photos from my D800, creating a simple HTML page to display them and uploading to my webhosting. There are several TODO items but it is functional. Run with -h for some help information.

---
- MultithreadProcessPhotos.py - A threaded processor.
- DuplicateCardsThreadedProcessPhotos.py - experiment that accepts multiple source locations and alternately reads files from each. Depending on bottleneck situations it could produce a performance boost.

---

## Requirements

- Python libraries: WAND for images, paramiko and scp for file transfer and remote zip file creation.
- Software also installed: ImageMagick
- On Linux Mint 19 and 20 I had to adjust the default values for the following resources of ImageMagick in /etc/ImageMagick-6/policy.xml. The defaults are fine for single-threaded execution but run out by 4 with 20MB source files. I didn't do a great deal of trial-and-error about these, though.

| name | value |
| ---- | ----- |
| memory | 2GiB |
| map | 4GiB |
| width | 128KP |
| height | 128KP |
| area | 1GiB |
| disk | 1GiB |

---

## Notes

6 threads is the effective limit on my setup in testing. The limiting factor appears to be the transfer rate of the CompactFlash card.

---

## TODO

- config file support
- better output webpage.
