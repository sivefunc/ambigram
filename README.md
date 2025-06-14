[READ in case you are using PYPI]: #
[Pypi doesn't render package/relative path images and not raw]: #
[Pypi doesn't render Emojis]: #
[Pypi doesn't render LaTeX]: #
[https://github.com/theacodes/cmarkgfm]: #
[https://github.com/pypi/warehouse/issues/5246]: #
[https://github.com/pypi/warehouse/issues/16134]: #
[Mainly it's because HTML tags are omitted according to theacodes]: #
[So I recommend you rendering mardown locally or check my gitlab/codeberg]: #

# :shipit: Ambigram
<div align="center">
    <img align="center"
        src="https://raw.githubusercontent.com/sivefunc/ambigram/refs/heads/master/res/Hero1.png"
        style="width: 100%; max-width: 400px"
        alt="Ambigram Word in the X Perspective"><br>
</div>
<div align="center">
    <img align="center"
        src="https://raw.githubusercontent.com/sivefunc/ambigram/refs/heads/master/res/Hero2.png"
        style="width: 100%; max-width: 400px"
        alt="Ambigram Word in the Y Perspective"><br>
</div>

# :bookmark: Table of contents
1. [About](#about)
2. [Installation](#installation)
3. [Example](#example)
4. [Notes](#notes)

## :question: About <a name="about"></a>
Ambigram is a small but powerful library that automates the process of creating 3D [Ambigram](https://en.wikipedia.org/wiki/Ambigram#3-dimensional) from two
different length (with spaces) strings.

## :file_folder: Installation <a name="installation"></a>

### :penguin: Binary dependencies (Unix)
```sh
sudo apt-get install python3 python3-pip python3-setuptools
```

### :snake: Option 1: Pypi
```sh
python3 -m pip install ambigram
```

### :hand: Option 2: Git repository (Still connects to Pypi)
```sh
pip install git+https://github.com/sivefunc/ambigram.git
```

## :computer: Example <a name="example"></a>
### Simple Text
```python3
from cadquery.vis import show
from ambigram import Ambigram

ambigram = Ambigram("HELLO", "WORLD")
show(ambigram.assembly)
```
| X Perspective | Y Perspective
| :---:  		      | :---:
| ![1](https://raw.githubusercontent.com/sivefunc/ambigram/refs/heads/master/res/HelloWorld-X.png)| ![2](https://raw.githubusercontent.com/sivefunc/ambigram/refs/heads/master/res/HelloWorld-Y.png)

### Two different length string with a Rectangular Base
```python3
from cadquery.vis import show
from ambigram import Ambigram

ambigram = Ambigram("ANDROID", "IOS")
ambigram = ambigram.add_base_rectangle(
    height=ambigram.font_size / 10.0,
    padding=ambigram.font_size / 10.0,
)
show(ambigram.assembly)
```
| X Perspective | Y Perspective
| :---:  		      | :---:
| ![1](https://raw.githubusercontent.com/sivefunc/ambigram/refs/heads/master/res/IosAndroid-X.png)| ![2](https://raw.githubusercontent.com/sivefunc/ambigram/refs/heads/master/res/IosAndroid-Y.png)

### Letter Support + Base
```python3
from cadquery.vis import show
from ambigram import Ambigram

ambigram = Ambigram("RECURSIVE", "FUNCTION")

ambigram = ambigram.add_letter_support_to_all(
    cylinder_height=ambigram.font_size / 4.0,
    cylinder_radius=ambigram.font_size / 4.0,
    rect_height=ambigram.font_size / 16.0,
)

ambigram = ambigram.add_base_rectangle(
    height=ambigram.font_size / 10.0,
    padding=ambigram.font_size / 10.0,
)
show(ambigram.assembly)
```

| X Perspective | Y Perspective
| :---:  		      | :---:
| ![1](https://raw.githubusercontent.com/sivefunc/ambigram/refs/heads/master/res/RecursiveFunction-X.png)| ![2](https://raw.githubusercontent.com/sivefunc/ambigram/refs/heads/master/res/RecursiveFunction-Y.png)

## :notebook: Notes <a name="notes"></a>
- Different Length String are implemented by placing the extra chars behind the shortest one (see it for yourself)
- Spaces are Allowed but needs further testing.
- A new algorithm for bases is need the current ones are rectangular and P2P, P2P is quite good at == string lengt but more improvement is needed.
- Needs further documentation
- Needs further testing

## Thanks to
- [2CatTeam](https://github.com/2CATteam/AmbigramGenerator) That allowed me to see that whitespaces and different string length are allowed.
- [Lucandia](https://github.com/Lucandia/dual_letter_illusion) That allowd me to see that It was possible in Python.

## Made by :link: [Sivefunc](https://github.com/sivefunc)
## Licensed under :link: [GPLv3](https://github.com/sivefunc/ambigram/blob/master/LICENSE)
