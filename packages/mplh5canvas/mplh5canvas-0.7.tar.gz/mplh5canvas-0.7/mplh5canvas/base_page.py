"""Avert your eyes :) A whole stack of HTML masquerading as Python. Aargh..

Anyway, we define a few strings (long strings) that hold the HTML served up at various points in 
our backend.

Copyright (c) 2010-2013, SKA South Africa
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
Neither the name of SKA South Africa nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

thumb_html = """
<html>
<head>
 <script>
  var thumbnail_ports = new Array();
  var native_w = new Array();    
  var native_h = new Array();
  function resize_canvas(id, width, height) 
  {
   // do nothing :)    
  }
 </script>
</head>
<body topmargin='0'>
<!--thumbnail_body-->
</body>
</html>
"""

thumb_inner = """
 <canvas draggable="true" id='thumbnail_<id>' style="height: 48px; width: 64px; border: 1px solid grey;">
  <script>
   function gen_thumb<id> () {
    var ax_bb = new Array();
    var ax_datalim = new Array();
    thumbnail_ports[<id>] = <!--thumbnail_port-->;
    var el = document.getElementById('thumbnail_<id>'); 
    var id = <id>;
    el.setAttribute('draggable', 'true');
    el.addEventListener('dragstart', function (e) {
     e.dataTransfer.effectAllowed = 'copy'; // only dropEffect='copy' will be dropable
     e.dataTransfer.setData('Text', <id>); // required otherwise doesn't work
    }, false);
    var c_t_<id> = document.getElementById('thumbnail_<id>').getContext('2d');
    c_t_<id>.scale(document.getElementById('thumbnail_<id>').width/<!--width-->, document.getElementById('thumbnail_<id>').height/<!--height-->);
    var thumbnail_content_<id> = "<!--thumbnail_content-->";
    eval(thumbnail_content_<id>);
    frame_header();
    top.plot_if_possible(<!--thumbnail_port-->);
   }
   gen_thumb<id>();
  </script>
 </canvas>
"""

base_html = """
<!DOCTYPE html>
<html> 
<head>
    <title>HTML 5 Matplotlib Canvas</title>
    <style type="text/css">
    body
    {
     font-family: sans-serif;
    }
    h1
    {
     font-size: 1.2em;
     font-weight: bold;
    }
    </style>
</head>
<body onmouseup="outSize();" onselectstart="return false" onload="connect_manager();">
<!-- Static images used on this page. B64 encoded to avoid seperate path loading... -->
<!-- base64 inline images shock! Page is not served from a standard webserver, hence the malarky... -->
<img style='display: none;' id="button_close" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAEAwAABAMBtJq7BgAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAPzSURBVDiNfZV/TNR1GMdf38/3TuBukHCAgMdxwBJisMMfEZPUtaGxcrFqSVY6kmYO+6NWW+VaK9vcWrlqS5p/iDZna1ZTtv5wWsM0CmZNhUPFkx93hyCdXxCuu+Pu+/1y/YF86YB6tuePz/PZ8/o8n/fz2fOR1u4+HGeBmWTBoxUOHi7MZLXdht1uQwJuj4xzdWSCTs9fXOzxoukzC1MxLQwU52XweeNGUkfGMPUOoP/aheYfAyA3fwV2Zx6Pu4oIPuni9aMX6B8ZT8iX5ioUksTuOhcNVYXQ2obW5110ekIlJQXwcj3fdPVz5GwPM/F4IvDVOhcNOSnEjpwGVf1fmGFmM+bGpzgZiHL4zFUAxNw1n68qInL0NLqmoguJlIYtxDPS0CUSPJ5mxbK9Di0eJ9I3yHjjezxbsZLivIxZoEkWHGzcSPR4G5qmoskSqa88g/WJDaS/2wS2NDQBmoCZB6wsf3MnlroarNs2E3L3MT0WILj3Iz5+cT0mWSBqyh1YRu4Q9njRJbBu3YSlpnJWp+wMbG83QUYaWixG+p4GzM48AFK3bsK2fy+qgMnOKyzrvk5NuQPTGqcN3TOILs3KMnm+i5S1ZSQ5cg1o9hs70UMRklc5DfmmPUOMfnkCVcyuY7904ardjFjtsDHtG0EXoAtQIxFuf3aUqH90XvuVKxJgEc8QvfXNhBUFVQZVhmDPDVz2dESBPZPwnTFDJ01ALBLh2q53CF2/taix04PDdD/dTPiugiowfPLmAIWOLExx4uhIxCXJSPr7+i1igXGQ5cVPRZbRzCZUISWExf184R1WMNuzjWcR9A4TVsap/P4Q1lWFi3jJjlxWn2pBXpmdUGFSWREDvgDisk9hmSMPXUBk8h5To6Os++4QqQ8VG5DQoJ+pGwPG2uK0s+6HFmR7tqGhxVXC1eEJxOUhBXNRAZqAcc8g9hfqSS2dhwX7vVx4bg8XG/Zwr/emEbc67RQ0bTMqtG6opts/gehw+4jl5JDitBMMBHB/9TUD37YZsPbtzQQVhdDUFOdfeo2J+1D/jz9x5ZMWVAHLH6lElJXS4fYh56zZ+sGfAwEadmym/+QpNF1juL0DSZK49OGnhBSFGQEzAtRYFO+Zn4nrOpf2H0SPzyBZkqhq/YK3jv+OMhWeHw67tlTwWFKYP/btR5+OLu7uEiYnJ7HuwPu0Ry20nu2Z7fLc5rFzbtqjFmrbTmCrqkzo4FJuq6qktu0E7VELx865jUOkhRO7OC+DAzvWE+m7wd3OTgLX+lA8sx22PVhEVlkJmdXVpJSUsu/4b/89YP9tJllQU+6gwpFORX46xflZAPT7A/T4J+jxTdDh9i35BfwDr1enT5ZTWAsAAAAASUVORK5CYII=" />
<img style='display: none;' id="button_close_over" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAEAwAABAMBtJq7BgAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAPpSURBVDiNfZVdbJNVGMd/57wt68e6jXXrurXrysCVbc6ADBDRhJiISIyLGiEQQ4hTQiY3akz0bnoraDSC4QbjhYmJH8TECyUaFogYPmLG5GNsbF3XfeDat1/vum5r375eDF5WRniS5+L8c57/85z/ec5zxKZDJw0eMKOok4leQ6gR9DujJBOTALhr/Fgb1mG4gzjq1yOk8mAolgeBXGKKZN8ptla6ea7Gx4bHt9NaVQvAzXSMG1qcv6f6uT5xkWJHF8LhLokXZoWGQfrfMxRuXeD45p1s8wRWZF9uA7MqR9UhNE87s+42QAAg721ID/xOe3yE87sPssUbQJc80tsr3JwMbmVHMYl3IWImkveOmR+6wBdPvYjVYkGXAvvenRjVFeiCEjcqnDj27aJgGOjhKfZfuUNTbgq7mF8iNIo6ib5TfLbtBSxWCwVF4HrrVZy7n2X1R93grqAgoSChWOmk6v0DOHZtx7nnebLXbqEn07x2Jcpm6xQCUBw1Tb0duRiH2rdgCHC9tAPXzqeXsjnt2Da2kv3nBoW0Rs17Byl7bEnbspYghtNG+uxFHHOLaI01/LfajaUYD/OMtxFd3NWy7yL2TW2UBeqX2sBTjefdA+jZHLaWoKnV/PAY0199R/7uLQQm4/jXgNRnwrTV1pti53M5Jj//hoXotBls9dWVkOWGx7je1cOcqpJXIK+AU83Q7JLIVGKK5ppaU6eChMVcjhtvfkj25u0V7TIfnmDglR7m4ip5iemWeApvbTkWMNCFQAphBs3evM1iLAHKypeAolCwWshLUYpLid3uQFZW+xhOxc220CITzKkJNvx4HGfLmhV8tkA9G0+fQPF5SirMN9aizYO0NbQwpCXQJeTSKTLT03T+cBxX61qTJBuOkhkcNdeOoJ/On06g+D2mhqzzE51XkJa6Zq4mYhQkJIbD+Pd34Vp/n0wbiXDu9cOc33uY1PUhE3cG/TR17zEr5MkOxtMFpMMbIqzrDCZjaLEY177+ltHvfzHJzu7rQVNVspkMfW8cIXmXNPrrH/R/eoK8BKWtGdrbGIgkURo6X+6lKsD4dD8hbQFDGEyc/QshBJc/PkpWVSlKKErILy4Q+e1PDF3n8ifH0I0ihs1Kfe8HfHluklR28f60caUHaU2O0BmZQRZXjMiHmlxlpeFIN5esXn6+NA4sm4daZYgxhwPhixEaDGNPZB5JVh5aS+M7b3MuOs/py1ETXzZgBTPWAFnpxb69DvdshoqZGDKRwlBTCGCV14OzqZHyDU9QFmrlWF+EaGy2JJF42BcgBfjKizSUw5oqC75aF3abnXTOIJoVjKfzXA0n0B8izf+Xmac2etmdhAAAAABJRU5ErkJggg==" />
<img style='display: none;' id="button_max" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAEAwAABAMBtJq7BgAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAN+SURBVDiNfZVbTJtlHMZ/3wGwVBhIWbGxjDMbwnAC0bCDuiWiS3YhlybsZsmmxuiNd8aIBO/MrrxZ4qJREy92pU6NyYynThonDGLHqSml5UxpCy2Utt/3fp8XbKWlxSf5J1/+h+f/vG/ePJ/UdfWGyQGoisyFZxvoaLXT2lhNXdURAIKRGDO+EKMPlvl9Yh5dGAdHkQ4SHnfaGHrrAmuPpXkgx5gXOyyIBABOpZQ6xUqbUc7R3SLe//QOvuVIYUJZknijv4e+s018rvuY0WN527PRqpZzWWngu1+m+fKHcQxzT5f6qOHqa92c6H2SD3fG0BDID/PdxdXUqBYAwiLFSGoNAK+IMMQWAy82cRn44vb9fcIWp41XzjYzFP8bHYGUpeRMiZ1TJdUATKejuBNLAEREEr8W43Zslt9e6OfPsQC+5QiqqsgMv3merxMedD2ZUZaBuX/xpmkwlwjh1zbZFKlM/t3oHa5fe4krQ9+inuusI6Tu4N0K5SjLYsl8RvQEE/EFgJzF7i0/k/Z2TrfXona22pnR1pGEXvDytey8YSBr6YJ9ruQcHY0OpNHAkvmjNEkwFeWU1cG5I00PhZnERYpmiw1bkRWATX2Xse2lHKJbG+Pc2pjgpNXBkOUiav3RSlYDYWTTwKZYeLrUXlABQIVq4XxFU05uNDaPrKWZ3VqgpaEK1TRMEBqSaYAhDiU7DJLQkbUUkqyACerceoSnisoI7oaJJGO4o16SQssMtJc7sRWX7R1ZSzC+NZ9DGNheRdbStJU7mV3ZQJ3ybVDbXMni9hrfL44w7PkmZ+Bm99u8XPMMANOxBQbc1/NUKkCn1cG0L4w8MbNOfbEdSdfxRQPIWjonst8hpplXfxS9jx9nai6M7PIEqaKSmuIykrvxvEbJ2CeUTKMg2XMVDbSUHOOuJ4isC4MPbvzB684+rIaJoqVyQjKzCfPrVsPk445rfPSZC10YKI6uS4PR+C6lxUX0n+zCtehG6GkkQyAZAk1oTEXmGFkZx70ygTfsy9QsksJwzzuMjsb59X5gb2m2fQ30tfPqmWMMuj/hn9V///e5dNd0MPj8e/zkCvDVz56MfeUZbKPjCQav9OKLz3Jv7R6ToVm8YT8AzVX1tFW30GPvobGshcGbfx1usNlQFZnT7bW01Vdyor6SZseefXmXQ0z5o0z6o9z1BAv+Av4D2HLBnnU1sUYAAAAASUVORK5CYII=" />
<img style='display: none;' id="button_max_over" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAEAwAABAMBtJq7BgAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAANnSURBVDiNhZXLbxtVFMZ/cz22M0mTOK7jR4lD4qRNrZaQqEFRJQQSiLJoQWIFLNghFgiBRP8FlohF6aYLBBJCLAKIBQukSixI2gaJhlSlJTQPbNcxiTNJPI4T2/O6LNranjgSR7rS6Nzzffc7Z865Vzn33jXJYZMOUl/moJSjtJ3BWM8A0D80Sjh2EqElUMIpUEQbVD3sENUt1m58RWhihMgbkwxNXCKUTgFQeZBlfylLfWEVe+UeMv4ibjDkwStPFCpSUs/Nkl+5yXNXLhM9P952eqvV7meoXPsZUx3E8A+3E9Yzv1LrKjJ95WN8HcFGwFSgn7iqAbDt1LlV32yyWjbmN7Ps/eNnw441UxbVLdZXbnDxl8/x+X3g2A3M88EYk8F+AJbMXeYP1gHYdepkrDL51+K8/nWOyq5Fxfaj4jqszX3J+U/fx68KsC1vbtL1fGerOhnTQHeqDffNC8e5OLfPXC6E6mw9IHx2kPjUaXCc9mLJZhPs2FUWyjkAWv/vRghKyQBJQ0GtGTlir6ZRWtJsNbvFL10HYZlHxuVjPk4VVFRDXyOdnkY4NpNdJ3ihd/SxMMmBazIc7GuAzmhRvh9520M0oy8yo9+h2CF4OaGhGoUskVQCYdtEfBpnOmNHKgAIqRovhUY9vtvlDMIyKSoWT0e6UaUExbFQhAT3iBr+jymOjbDqCASapqGGB4YwVvKETw2wUyvze2mNil1rAM72JIkEugEoWQcsGhkPYbaygbBMBkUf25aLGkmMUVkpEBmJc71wm0/+/NYD+GLqAy7EJwBYKj/knfnP2lT6gLGuMBsbDoJjA5TuFVBsm6yRR1imZ3n7ULbtP1nngikeFqsI9fgIZqGK/lcWfa/YFqi4TUJFukeSPROIMxYY4o9VHRVFQPIVdn+6hXoJpO9Q0WUrocRn1T37AeHn8uCbXJ35G9txH82yGwxhypOkFnJkxyu4ojkdPy5f587mfQAK+1uexg4IPx+l3uK3uwbZzfKjQ5sXrCRKgcSxHZaG8mx3VNqK32rp3hQfnn6X+bt7/DC7inw8oi0XrEKRpzio9jO9HaXWW0HXttCVErpbAuBER5Th7iTjfc8y2p3m6nfLDWUNlqOeAKFAsgcSfYJk1M9gpIdOrZOdmsu/JcgV6yyu6diOexjKf/dLl8SuHWsnAAAAAElFTkSuQmCC" />
<img style='display: none;' id="button_resize" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAEAwAABAMBtJq7BgAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAOhSURBVDiNfZVLTFxVGMd/99zLMMy0PGZ4F6bA8Ia+tY0lscZGqZFFk+60gQWG7mriWppqWxcmmlTdNLE1ttW40Jq4MEpqQmOpxjYoQkEYec2Y4TUMDJnXfc24GB0GmPaf/Hf3/M7/fN+535GO9F1Lsk2KLOhod9FaX067u4L6ikIAZpZCTMwsMjLpZ2jMi2Emti9F2g50Vzp459zLLCctTEVhLmLii5oAVNtkauwyjTYokzQuXBtg2h/MDhSSRPcrh+k60cbteZ3JDWPH7plqylc4uzeH7wbHuP3D7ySSqVzK/x90nzrE/meaufxnGN0E8VQceIIml0Mqrx9poUeCz74fBv5b5650pJJNhnm+1MJpl5VjTgWXFSwJE8nI7oV1lbfuBzj5XAvuSkcqoSIL3u17ia8mIxhxA2eO4FX3rnSSZBICMZOFiM5C2OCeL8KgN8psSCOspZry5mCAD3tP0vveNygd7S5WVAnPShQJWNhQgU2gJEGJTabEJhNWI9x4uEzMSG4eD/h1NsR4i52OdhdKm7uM6aCGZKQ6ubgez1qzX7xhznzhQTUSCKDYphCIbjbu/nyEfbWliLbacnzBGMIwEYbJ0nqc5I6bCfvL8yjNSSJrOp01dj49XYOs6WmP+jZo3luGaKgoZHE1ijAMhGGgx3XWYvoOoN0i8+D8AXoOOrn5WhP7ym0ITU97yheicU8RApKgm0gZnl2OAvCzZ42YZm6BfnCmAYss4bDn4FRAqDpC1ZFUA0gi/vavU7U7J30VAsEowzPrDI4H6P7kES9cGtoCzVSTIzedsLU4l6l/gojxuSVcRbkIwyQaVnk0scy3Q17e+Pg3jIiKf2GDC18+zgpsLLama3ig0s5f88uI0ekl6kryEKbB9PwaiZjGY08APaIiNJ0Xmx1cOdueFdhQmpdOeLyhkIm5FcTQmBfHboXaYht+f2hLoZ25gr5TbqLx7P+1u3wXQtM5VldI4x47Q2NeFMNM0H/9J94/18n1r0eJZ9RrQ9Xp6b8LgLPASn11AfVV+dRXF+CuKiDfqmBPJrjSe4i3b9zFMBOb06an8yCuIif9Hz3YAn2arBaZS+eP411b5fMf/wAyhsqtgRG8wVXuXO3iaJNzy9Gz+WiTkztXu/AGV7k1MJLeJOuAvdh9gumZNR4O+xmfWsEzu5pqQq2T1sYSnj1cibuuiIs37z15wGYq/QS4immpLqGhOjWaPL4gE74Vxr2BJz4B/wKrEccDtJ7HywAAAABJRU5ErkJggg==" />
<img style='display: none;' id="button_resize_over" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAEAwAABAMBtJq7BgAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAOaSURBVDiNfZRLbBtVGIW/uTO2JxkTv52keTZOSBy1oRIVqEARgoqHuinqAlGhdIO6RIJFxQY2iAWLIlWwAAmxABGxqITEgk15BKEQqZQCah4iIS11EqdxjV8Zj+15eFhU2HFs8Utnc6X/3POfe/8jPXzhY5cD5dYdiqklKvktjOI2lUwKAH/vKFp4ADU4iH9gGknIB1tRDh5UcmlSi3OEp2YYeuYUocljBMeSABRurVLaWKKwdI3ijTl6ki8gtGhLv9RQ6LrsLn1HYfM3HnvzMvGZE22376+99T/YmruECI5Rj0wDUivh7s2ryGqdJy5eRvap/0vWsMYy2f36I8ySxV7XYQDEf2MWU79z8o33eXa0hzPDKo9GFIZV8NYdJLsz/qm6bB6fRZOK+Fzjvodu3SG18AVPvv4eHqEQ8QhOJ/xNFS5kKw47ZYsd3ebHzTLzKYPbRRPdrANgTLzI4+mrrDkJlGJqiWhimr6p4+A47JRqQJNQkiDWLRPrltFrZT79JUPFdpvjAXlPL3pgkJheRVRymwwePdEY426h2tGvxZTO2c/XqBkmwrSIKy7CtBq45xsg1O0iqrktYqNJhO0gbIfdQhW37WfCTF8XcY+LbFo8N6rxyZlRZNNqoOD2EH/AgyhnU0T7xxC2jbBtrKpFvmK1EWpemZ9fe4jzxyJ8dm6So33dLQrzNR/9AS9CckGynBbcztx/sZ/W81RMp4X00tkJvLJEWPMQUUDUrAZUnw+hxYbIp9YaHmZzBjduFZhfyTL74XWeemehhXR/TYZ9DYX9coU9x4vQoiMUN/9E2A6GXuP6aoavFlK8+sE17HKN9E6Jt+eWOxI+GFUbHo5oDjkDRFd0mOzfNxGOzcadPPWKyfJ6FqtcQ5gWT0+FefeVIx0JJ+JdDYXJGGR0B6EdSqLn0uTurJJOF1uMjvgEF55PYFTtjoSJPj/CtBgPOIzFvazdNVAkIaMdOc1fi18iQi8hSc0AKtUszr/1LQCRgMr4UIDxwR7GhwIkBgP0qAqqbTN7MsyVXzM4dbcZDkp2GdmokhWP4NKec53Ko0i8fCpEybX5fjkLNLcHOzqNJxwk6V8kKOVaRu+ERFTi4rk4Jdfhh5Vs45J9ASuh+xPYbj/J0DaWpVPUNUqGl4IuIwHRkOBQr5eJw36GR/xcuXGPnQOr2pbYVambFXecmFYlGnGZ1qAvqKCqPkqWh1xNYkO3+GZ+G6fevqP/AuWCyZZYcPwAAAAAAElFTkSuQmCC" />
<img style='display: none;' id="button_home" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAEAwAABAMBtJq7BgAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAANvSURBVDiNjZVdTJtVGMd/79tauvLZFoaAfJQP040CUmYmA0TishCTGXXJIjEmxk2vjd5suzC7WmI0eqdRkwW3C40X6p2JJBKJjBgWt0ExE6G23cqg3Whrx1ffc87rRUs3GApP8r865/zO85Xn0bre/txkm1ktOj2+Op5uLsfvcfNElRsNiMYSTIcTTPy5xNhUGCHV9qdo24FN1S4+eauPkrUlrLEgcnkBmVwCwFJWicVVjahs5r6jkne+GGMuem9noK5pnB5sZ6i3ESZ/QCyFHrqlgZn9V7PaQNexuGvQDr3I17/O8+WPU6jcuaW66/h5gNOD7bzaaifz8yXkP8uYZpZhahaKn38NbPsw4lGKBoYo7D2BWk2zNvYNHZ1tOFwVTM4uAqBvhjnU28j6+HdII4NUKisTivpPYqv1UtR9HFtzJ2bOE6UU63dCLF88y0v+KpqqXVmg1aLz0aleMhPfIzIGQpKTRnHfCewe32bclPS9gmYvBGB9MUx69gZrsQXSl9/ngzeOYLXoWHt8dThSUVaiwS3JdT37Mo4n/dtKqGPbX5v1UEgMka1y6o+rlEcD9Pjq0DvqnajFIFKSV+nhFyhqfeaRltiEAljd1RjCzCszc4WOeie63+NiPbaQz1tJ1wCl/v6dYQ9Zqf857C2dGFJhSEV6foaO+jL0hpoKVuN3EBKKfUdwdw/uCgPQC+x4z3yGvaEVQ5ik/p7FU1ORrbKUJtI0WY0vEPr2U+Tayq5AUwqunz/Fxv0VDKEQuXzqwdtxHnM9jhQm6XCQ+O8TyI313YFKcTdwjWRoDkOYFNS0ELwdR78WWsZWUYVUio3VFWLTk/le280282dIhaPxADciSfSpcAJLZQNCQTI0T2ZD7AkGbKlyYXsvU+EE+nggguGuw1FVTyoawRCKvfkHhlAYQlF2sAvd0854IIIupOLMV1eoPHYSoXQMYbJXoiFMlKWAg+99yNlLEwipHkybN4/5GChOcPXCu+hWK1qugf/bTKRhcOjcx4ymnVz8KQDkhgPA8MgMo2knR4dHKGk8wEoy9b8q9ng5OjzCaNrJ8MhM/psdB+yF17tZ++s6d3/7hfjNAPfmbgLgbvZS4fVRfriffS1Pce7yBPMLy1v8fgQID1ZAW52TttpSmmr3AzB/K8b0rRTTkQTjgciOK+Bfa+a4GLtdYmQAAAAASUVORK5CYII=" />
<img style='display: none;' id="button_home_over" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAEAwAABAMBtJq7BgAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAANtSURBVDiNjZXdT9tVGMc/59fS/aAvvJettALDAnMYFTTbVGTTGHWJibpsiTOaqIm36oWJd+4/WPRiaqL/gGYX3umlGDSZOnWQiGy8tJXCaPtrKRRafufFi0IHjAhP8tycPOdzvs9znvMcMfzel4Y9ZrSimJyEwjw6N4uTSSOAcKSLhsgAMhjDF46DsPZuxbt3YcNJ44x/zemuFp4djPFo91OciLYD8M+iw99phxupW0xN3aTc8xLabtq1X9QUGkNh8gfk3DjX3n6BM32xHVECTDVMeH1gWUymlvl0fI6V0ACOPw4IADyR4ZevADgT3zNoZrj+wUW62psxpsowwkPwuTfAV4+bWSBw7nX8T1+gPRTgrL9IvpijpARFQvdS3nDSqLmf+eyTt6jzWiitt5RZNI5ewhcbwBfrR7ubmC2lWmt0Ls3FugWWK4Kcp411fQTLaEX2p6+4+ubzeC0vUrHlguDIBeyewe28CY28hrD9AJSXEqxO/4UqZHnF3OZUcBFLgHclOclwJMTjxzvvKQNannmVhr6h3TcmLHzham21VLiyGt8q8/RSYNovsdzMDCP9UZSi5o2nzhM4efq+ltiGAnhbI7jS1DxaXiIaAEvnZnkodhSlNUprQsPnaBwa3R+2wxqHzmLHH8NVGldp/CWHniaBVXQWOR5uQyoIDj5J65kXD4QBWEdsBj7+HLv7JK40eIo5jrUGsIyhqs4Y1jNp5r+5htooHQg0SvLnlXeprJVwpUZKjW3bWC3hGHeWCihpWE3Mkrn5C6pSPhioNdnJPyjM38GVhs1QB6sVsHxH+7i97KC0prJeYnni11qvHWTb9XOVho4HSK15sHzhXm6lHaSGwvwMmxV5KBiw65bFg8MkVhSWHY4zV/YwfTfPykISV2oOpw9cqXGlxhONY7oeZiJRwEJYqPh5vp1eZr0scaXhsERXGqSoo+nyh3wxtoDSpvqWjd1MsfkEN+oMQ9kprl8aRewz63abQVpejl1+n7Gk5N9stTNq87AY7GOuvgETjtI//zv1hez/4vy9A/S88xFjSZfvfluore8YsIK73hhrVgf1Qx20ljIEMyk8+Qwmn0EAvo5OGmI9NAw+gS/+CFd/TJPKru06SOz3BVgCIgFNp9/Q3SiItAWx622KG4ZUyUNyRTGRyKP0/cX+DwdjpAeUBIzPAAAAAElFTkSuQmCC" />
<img style='display: none;' id="button_pan" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAEAwAABAMBtJq7BgAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAPLSURBVDiNfZVdbFRFGIafmfO7p2Xtj+y2lP7xY5u2glEhhhBBYqQixVCjlya900QTSOCKGEkM8UYTEky84M54aUgshGjSgBjEGAmxtJC2CC1LS9vddlv25+zuObtnvICulq58yXs388w733x5R1ChlFIG8E7Ozb7h+/5ey7I3A/heYUo3zGt2KPQTcF4I4T+9V1SA9bjZ7OBMLBaN3b0bis/NicV4HID6SIRIQ4Nq27Il19TSsmg7zkEhxM2KQKWUzOdyn3sF78jQ4IXww9iDSubLtaGlmTff7UubpnHaDoVOCiGCVUA3656cmYodv3ThZ6foFwHo3NbN9FSMTCpdEaobOvsO9rob21tOh5zQCQC5ck2v4B29fOGSExQFUhjous2+vv109HQjhbFGBBrx6QW+PXXGcTPZj5RSPQBSKWW4GffHX85fDquSRAoTKUyE0h/3RGi8/X4fL722AylMchmf+xMz/PX7KJNj0ywnspz98mydm3HPKaUMCRyYvT8bTTxMrnIgeAJEoz7yPM/V1BBpaOT13r0sxzMYMoQubHRhc+9WjPHhiQhwQObd/O65WMJZcabrdtnl49eSlIoBj5IZGpobae9s5/BAPwPHBtBkqKzb1yfCeTe/W/e90r6lRFpIYWA7Fh98fIjRP8e48esIKlBYlo1u6LRubX7SAkF1OEzVumo0YZcfaOZuQniF4h5p2eYLjxZcpDDxcopsOkf3jk48VxEEAdt2dVEVdmhsjdLYGqV2fQ279r+KEHKVw/lYCss2OySAFAYaj3Vv5AGaJvnw+GE0XfvfORRo5R6uCED6heJE3fp6pDSR0mTk2hRBoLCrrGcOtu8Fqxw2tTfhF4rjUjf0S3XRGiUx8fOCsT8e8tvg6DNhAJMj82jCLqt58wZlmMYVaTnG1fUbarNSGizN5hHYDH0/yuTo/DOBd24kVjnseKU1ZTnGVQlcjLbVztU31JJOlNCFjVQWP3x9ndRiriJsYTpNOl4s925T10Y2vdgQBy5KIYQfqjIO7+zdtKxr/55YyEiGvhuvCPz7xkJ5nWVX897RnUm7yugXQvjlcCi4xc8mh5PHBr+5HS56AQBSE7z8VhMASoFSChRMDidZms+hm5JDn3Sl2rfXfWU5+hfwVHx5udKJgls6cv7MnbrpscoJs1IbO9fR9+nWpOVop82QdmpNfP0H3FPIls7FbmUiU8Op8PykKxYf5AGob7aJtjuqbXs41dJdHbeqtH4hxKqRWAN8AjWAA14u2F30gj2GJTsA/EIwrpvyihmSV4GLlb6AfwCPPIOQNBOBtgAAAABJRU5ErkJggg==" />
<img style='display: none;' id="button_pan_over" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAEAwAABAMBtJq7BgAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAPVSURBVDiNfZVNTFxVFMf/9777Pu59D2bKDAMzzhSZwcGREmz7wBgiVWO0qWMbN8avEnVR6YIaTOzCFTtduNTFGBcmBtO4oCsILogL40LMtEqjRGwpHYEB5iNQeDPM53MxYaR8neQk772c+7v/c97N/xIcHjKAC4LzfllmLxYKxTClRHI6nAmX2zVTrlQnhBA34/F4af9CcgjslKooP4RDoZaucNjp9/mo1+MBAKxnMlhPp5FMp0ub29sbXp8vOj4+PnMUkBJCrjfoxscfvPGWM9TeLh+hHgCwlknj9/m5gi70byKnuq6Njo5WAYDtqfkk0hEevvL2+82yXGP5TvoBACuJpQNAr9uHlqZWdS5x92pmLWUAeA8A6G6bhtCHh9694lMVAUpkUCKjb6Affef66+/703q4AzXHaD6/8+bw0PCZXYUyk9jY0DtXnaqsH1BCQNFtnkHbE22YvDGBYqGI1GoaqeQ6CvkCAEASkspDfCIWi52kAC4EAyGjMxjR9yuATQAQuDwuuDwu2BWKS5dfh5XNg0EFIxoY0UDyMmiRtWZWMoMUgNkd7tEoUUCJAsY07D4DBIQQ7ORKKJcq4KIBgZAf5sAz+HzsM0iU19POUShMO88ISG8k1N1MSe1HXBx8BZVyBZNj06hWAFlh0A0Dqqbg7HOnAQCGwwFhcEhEq4+mkmMQDfppRiXpbHsgLO8Cs2ub6Ohugz8YwPZmHv6QF80+FwCgq7cTABC9/FJtdpTXgWWLwHGi8TEG27YpZEioAe/+8S86utswEO2FxCiOC7ZHISEEnHNQiUm3lpLLJUoVUKpgLfEQycUMZJWBSkcDS8XyIzNsdDVCgrpEhRAziysLKQoFFAoSf2Ux9e1vsG37WHULs0lIRKtnk9cJBvU2FULE7yfnc5TK2N4oo5ijWJjNYvr72WOB87dWH1HYGmyCrutT1Ov1Tmatla3E8qK1lSrXz9YvN+/h75nkkcB7tzL12uaAA/6wK2m0SN/ReDxeEjofnL5zI1uw7P93JRyTX8+hWjnYeiqxhe1MrVZWBMxLvh2D86hpmqW620Sj0eut4skPH7dfDtI9nhF51gPdqcC2Adg2bBtIL1tI/LkByoCeVxsr7oD+Ve+5yEfAHrcxTfOLB/cfYJVPXWvNveCSC24NAOZ/3Tq05aaAwNMXhaVx/mVPX8enu98PGOzIyEiXoTvGjHKgWcn7PCTXyKpW7QCrzgp0TxXudmmnpUNbc7nFa8HO4J296w9zbMRiMblQKJzXVNHLlYbnuVCf4pqQVFn/Rwj+84kW/pNlWT+apnngCvgP+TAum4t9Kv4AAAAASUVORK5CYII=" />

"""

base_html_decoration = """
<span id='title'>
<h1>HTML 5 Canvas Matplotlib Backend</h1>
</span>
<table width="100%" border=0 cellspacing=2 cellpadding=2 style="margin-bottom: 0; position: absolute; left: 8px; top: 38px;">
<tr>
<td style="height: 50px; -moz-border-radius: 5px; border-radius: 5px; border: 1px solid grey;">
<iframe name='thumbnails' id='thumbnails' style='border: none; height: 54px; padding-top: 3px;' width="100%">
 <!--thumbnails-->
</iframe>
</td>

<td width=200>
 <table cellspacing=5 border=0>
 <tr>
  <td>
  <div onclick="set_layout(1);" style="cursor: pointer; -moz-border-radius: 5px; border-radius: 5px; border: 1px solid grey; height: 22px; width: 40px;"></div>
  </td>
  <td>
    <table onclick="set_layout(2);" cellpadding=1 cellspacing=0 border=0 style='cursor: pointer;'>
     <tr>
     <td>
      <div style="-moz-border-radius: 5px; border-radius: 5px; border: 1px solid grey; height: 20px; width: 20px;"></div>
     </td>
     <td>
      <div style="-moz-border-radius: 5px; border-radius: 5px; border: 1px solid grey; height: 20px; width: 20px;"></div>
     </td>
    </tr>
    </table>
  </td>
 <td>
   <table onclick="set_layout(4);" cellpadding=1 cellspacing=0 border=0 style='cursor: pointer;'>
     <tr>
     <td>
        <div style="-moz-border-radius: 5px; border-radius: 5px; border: 1px solid grey; height: 10px; width: 20px;"></div>
     <td>
        <div style="-moz-border-radius: 5px; border-radius: 5px; border: 1px solid grey; height: 10px; width: 20px;"></div>
     </tr>
     <tr>
     <td>
        <div style="-moz-border-radius: 5px; border-radius: 5px; border: 1px solid grey; height: 10px; width: 20px;"></div>
     <td>
        <div style="-moz-border-radius: 5px; border-radius: 5px; border: 1px solid grey; height: 10px; width: 20px;"></div> 
    </tr>
    </table>
 </td>
 </tr>
 </table>
</td>
</tr>
</table>
"""

base_html_canvii = """
<span id='plot_canvii'>
<span id='plot_canvas_0' style='position: <!--canvas_position-->; top: <!--canvas_top-->px; left: <!--canvas_left-->px;'>
<canvas ondragover="onDragOver(event);" ondrop="onDrop(event, 0);" style="border: 1px solid grey;" id="canvas_0" width="640" height="480" onmouseup="releaseCanvas(event,0);">
</canvas>
<div id='button_menu_0' style="-moz-border-radius-bottomleft: 5px; border-bottom-left-radius: 5px; -moz-border-radius-bottomright: 5px; border-bottom-right-radius: 5px; background: #336699; border: solid 1px grey;  top: -1px; position: relative; width: 640px; height: 20px;">
 <table width="100%" border=0 cellspacing=0 cellpadding=0>
  <tr width="100%">
   <td width="24" style='padding-left: 2px; padding-right: 10px;'><img onclick='close_plot(0);' onmouseover='this.src=button_close_over.src' onmouseout='this.src=button_close.src' style='cursor: pointer;' id='cb' src=''/><script>document.getElementById('cb').src=document.getElementById('button_close').src</script>
   <td width="60%" onmousedown="clickMove(event,0);" style="cursor: move;"><span id="status_0" style='color: white;'>Disconnected</span>
   <td width="35%" onmousedown="clickMove(event,0);" style="cursor: move;"><span onclick='change_cursor_info(0);' id='cursor_info_0' style='color: white;'>Cursor</span>
   <td width="24" style="text-align: right; padding-left: 5px;"><img onclick='pan_toggle(0);' ondragstart="return false;" style="cursor: pointer;" id="pb" src="" /><script>document.getElementById('pb').src = document.getElementById('button_pan').src</script>
   <td width="24" style="text-align: right; padding-left: 5px;"><img onclick='go_home(0);' ondragstart="return false;" onmouseover='this.src=button_home_over.src' onmouseout='this.src=button_home.src' onclick="maximise(0);" style="cursor: pointer;" id="hb" src="" /><script>document.getElementById('hb').src = document.getElementById('button_home').src</script>
   <td width="24" style="text-align: right; padding-left: 5px; padding-right: 5px;"><img ondragstart="return false;" onmouseover='this.src=button_max_over.src' onmouseout='this.src=button_max.src' onclick="maximise(0);" style="cursor: pointer;" id="mb" src="" /> <script>document.getElementById('mb').src = document.getElementById('button_max').src</script>
   <td width="24" style="text-align: right; padding-right: 5px;" onmousedown="clickSize(event,0);"><img border=0 onmouseover='this.src=button_resize_over.src' onmouseout='this.src=button_resize.src' ondragstart="return false;" style="cursor: se-resize;" id="rb" src="" /> <script>document.getElementById('rb').src = document.getElementById('button_resize').src</script>
  </tr>
 </table>
</div>
<div style='cursor: crosshair; height: 0px; width: 0px; border: none; position: absolute;' id='limit_div_0_0'
    onmousemove="slideCanvas(event,0);"
    onmouseup="releaseCanvas(event,0);" ondragover="onDragOver(event);" ondrop="onDrop(event,0);">
</div>
<div id='zoom_div_0' style='height: 0px; width: 0px; border: 1px dashed grey; position: absolute; left: 0px; top: 0px;'
 onmousemove="slideCanvas(event,0);" onmouseup="releaseCanvas(event,0);">
</div>
</span>
</span>
<div style='position: absolute; display: none; border: 2px dashed grey;' id='resize_div'></div>

<script type="text/javascript">
    var sockets = new Array();
     // holds the collection of sockets for this page
    var contexts = new Array();
     // holds the contexts for this page
    var canvii = new Array();
    var last_frames = new Array();
    var last_id = 0;
    var base_span = document.getElementById('plot_canvas_0');
    var ztop = 0;
    var base_port = 4567;
    var management_socket = null;
    var canvas_errors = new Array();

    var free_frames = new Array();
    free_frames[0] = 0;
    free_frames[1] = 0;
    free_frames[2] = 0;
    free_frames[3] = 0;

    function plot_if_possible(port) {
     // are we plotting this frame ?
     for (var i=0; i<last_id+1;i++) { if (free_frames[i] == port) return;}
     // if we have an empty / stopped canvas then plot this up
     for (var i=0; i<last_id+1;i++) {
      if (free_frames[i] == 0) { 
        start_plotting(i, port);
        break;
       }
     }
    }

    var layouts = new Array();
    layouts[1] = [10, 105, 800, 600];
    layouts[2] = [10, 105, 640, 480, 660, 105, 640, 480];
    layouts[4] = [10, 105, 453, 340, 477, 105, 453, 340, 10, 474, 453, 340, 477, 474, 453, 340];

    
    function set_layout(t) {
     for (var i=last_id;i<t-1;i++) {
      add_canvas();
     } // make sure we have enough canvii lurking
     try {
      for (var i=0;i<thumbnails.thumbnail_ports.length;i++) { plot_if_possible(thumbnails.thumbnail_ports[i]);}
     } catch (err) {canvas_errors.push("set_layout(" + t + "): " + err);}
      // see if this gives use any more plotting opportunities
     for (var i=t;i<last_id+1;i++) {
      document.getElementById("plot_canvas_" + i).style.display = "none";
      stop_plotting(i);
     } // make sure non used canvii are inactive and not visible
     for (var i=0;i<t;i++) {
      var plc = document.getElementById("plot_canvas_" + i);
      plc.style.left = layouts[t][i*4] + "px";
      plc.style.top = layouts[t][i*4 + 1] + "px";
      do_resize(i,layouts[t][i*4 + 2],layouts[t][i*4 + 3]);
      plc.style.display = "inline";
       // in case we have any data for this canvas..
     }
     // see if this gives use any more plotting opportunities
    }

    function maximise(id) {
     var w = document.width * 0.98 - document.getElementById('plot_canvas_' + id).offsetLeft; 
     var h = document.height * 0.98 - document.getElementById('plot_canvas_' + id).offsetTop - 20;
     resize = id;
     do_resize(id, w, h);
     resize = -1;
    }


    function add_canvas() {
     last_id += 1;
     var sp = document.getElementById('plot_canvas_0').cloneNode();
     sp.id = "plot_canvas_" + last_id;
     var t = document.getElementById('plot_canvas_0').innerHTML;
     t = t.replace(/0\)/g,last_id + ")");
     t = t.replace(/\_0\"/g,"_" + last_id + '"');
     sp.innerHTML = t
     document.getElementById('plot_canvii').appendChild(sp); 
      // position new plot
     var pc = document.getElementById('plot_canvas_' + last_id);
     if (last_id % 2 == 0) {
      pc.style.top = 100 + ((last_id / 2) * 530) + "px";
      pc.style.left = "10px";
     }
     else {
      pc.style.top = 100 + (((last_id - 1)/2) * 530) + "px";
      pc.style.left = "660px";
     }
     document.getElementById('status_' + last_id).innerText = "Disconnected"
     canvii[last_id] = document.getElementById('canvas_' + last_id);
     contexts[last_id] = canvii[last_id].getContext('2d');
     if (!(last_id in ldiv)) {
      ldiv[last_id] = new Array();
      ldiv[last_id][0] = document.getElementById('limit_div_0_' + last_id);
      ldiv[last_id][0].addEventListener('mousedown', function (e) {wrapClickCanvas(e,this);}, false);
      frame_counter[last_id] = 0;
      frame_start[last_id] = 0;
      cursor_info[last_id] = 0;
     }
     zdiv[last_id] = document.getElementById('zoom_div_' + last_id);
    }

    var ax_bb = new Array();
    var ax_datalim = new Array();
    cursor_info = new Array();
    cursor_info[0] = 0;
    frame_counter = new Array();
    frame_counter[0] = 0;
    frame_start = new Array();
    frame_start[0] = 0;

    function change_cursor_info(id) {
     document.getElementById('cursor_info_' + id).innerText = "";
     cursor_info[id] += 1;
     if (cursor_info[id] > 1) cursor_info[id] = 0;
    }

    function exec_user_cmd(id, cmd_str) {
     var ret_str = "";
     try {
      ret_str = eval(cmd_str);
     } catch(err) { ret_str = "user command failed: " + err;}
     if (id in sockets) {
      try {
       sockets[id].send("<user_cmd_ret args='" + ret_str + "'>");
      } catch (err) { alert('error returning output of user cmd:' + err); }
     }
    }

    function draw_frame(id) {
     try {
      if (frame_counter[id] == 0) { frame_start[id] = new Date().getTime();}
      var c = contexts[id];
      //if (id in sockets) ldiv[id][0].style.display = "inline";
      //else ldiv[id][0].style.display = "none";
       // when in client mode we cannot zoom anyway...
      for (var i=0; i < ldiv[id].length; i++) ldiv[id][i].style.display= "none";
       // hide any existing limit divs...
      ax_bb = new Array();
      ax_datalim = new Array();
      eval(last_frames[id]); 
      frame_header();
       // execute the header. This will perform initial setup that is required (such as images) and then run frame_body..
       // we need a zoom limit div per axes
      for (var i=0; i < ax_bb.length; i++) {
       if (!(i in ldiv[id])) {
        var nid = 'limit_div_' + i + '_' + id;  
        var ndiv = ldiv[id][0].cloneNode();
        ndiv.id = nid;
         // fix the id
        ndiv.removeEventListener('mousedown');
        ndiv.addEventListener('mousedown', function (e) {wrapClickCanvas(e,this);}, false);
        document.getElementById('plot_canvas_' + id).appendChild(ndiv);
        ldiv[id][i] = document.getElementById('limit_div_' + i + '_' + id); 
       } // we need a limit div for this axes
       ldiv[id][i].style.display = "inline";
       ldiv[id][i].style.left = canvii[id].offsetLeft + ax_bb[i][0] + "px";
       ldiv[id][i].style.top = canvii[id].offsetTop + ax_bb[i][1] + "px";
       ldiv[id][i].style.width = ax_bb[i][4] - ax_bb[i][0] + "px";
       ldiv[id][i].style.height = ax_bb[i][3] - ax_bb[i][1] + "px";
       frame_counter[id] += 1;
       if (frame_counter[id] > 30) { 
        fps = (frame_counter[0] / (new Date().getTime() - frame_start[id]) * 1000);
        if (cursor_info[id] == 1) document.getElementById('cursor_info_' + id).innerText = "FPS:" + fps;
        frame_counter[id] = 0;
       }
      }
     } catch (err) {canvas_errors.push("draw_frame(" + id + "): " + err);}
    }

    var last_manage = "";
    var server_port = <!--server_port-->;
    function connect_manager() {
     if (management_socket) management_socket.close()
     management_socket = new WebSocket('ws://<!--server_ip-->:' + (server_port+1) + '/');
     management_socket.onmessage = function(e) { 
      last_manage = e.data;
      eval(e.data);
     } // end of function(e)
     management_socket.onopen = function(e) {
      management_socket.send("update");
      <!--requested_layout-->
     }
    }

    function update_thumbnails() {
     try {
      document.getElementById('thumbnails').src = "http://<!--server_ip-->:" + server_port + "/thumbs";
     } catch (err) { canvas_errors.push("failed to issue update thumbnails"); }
    }

    function start_plotting(id, port) {
     free_frames[id] = port;
     //if (!(id in sockets)) {
      sockets[id] = new WebSocket('ws://<!--server_ip-->:' + port + '/');
      document.getElementById('status_' + id).innerText = "Connecting to port " + port + "..."
      sockets[id].onmessage = function(e) { 
       document.getElementById('status_' + id).innerText = "Connected"
       if (e.data.indexOf("/*exec_user_cmd*/") == 0) {
        exec_user_cmd(id, e.data);
       } else {
        last_frames[id] = e.data;
        draw_frame(id);
       }
      } // end of function(e)
     //} // end of if id in sockets
    }

    var allow_resize = true;
    function resize_canvas(id, width, height) {
     if (allow_resize) {
      if (id >= 0) {
       canvii[id].width = width; 
       document.getElementById("button_menu_" + id).style.width = width + "px";
       canvii[id].height = height;
      }
     }
    }

    function stop_plotting(id) { 
     free_frames[id] = 0;
     if (id in sockets) {
      sockets[id].onmessage = function(e) {};
       // reset the handler so that the buffer behind this socket does not polute new plots
      sockets[id].close();
      sockets.pop(id);
      last_frames[id] = "";
      document.getElementById('status_' + id).innerText = "Disconnected";
     }
    }

    // create the contexts for our canvii
    canvii[0] = document.getElementById('canvas_0');
    contexts[0] = canvii[0].getContext('2d');
    
    var zdiv = new Array();
    zdiv[0] = document.getElementById('zoom_div_0');
    var ldiv = new Array();
    ldiv[0] = new Array();
    ldiv[0][0] = document.getElementById('limit_div_0_0');
    ldiv[0][0].addEventListener('mousedown', function (e) {clickCanvas(e, 0, 0);}, false);
     // this style of event listener is an issue in Firefox 3.7. Will need to fix at some stage...

    var native_w = new Array();
    var native_h = new Array();
    var zdraw = -1;
    var resize = -1;
    var move = -1;
    var startX = 0;
    var startY = 0;
    var stopX = 0;
    var stopY = 0;
    var rStartX = 0;
    var rStartY = 0;
    var mStartX = 0;
    var mStartY = 0;
    var pan_mode = false;

    var top_e = null;
    function wrapClickCanvas(e, ref) {
     var p = ref.id.split("_");
      // extract the figure and axes ids
     clickCanvas(e, p[3], p[2]);
    }

    function handle_user_event(arg_string, id) {
     if (id in sockets) {
      try {
       sockets[id].send("<user_event args='" + id + "," + arg_string + "'>");
      } catch (err) {}
     } 
    }

    function handle_click(e, id) {
     if (id in sockets) {
      try {
       var pc = document.getElementById('plot_canvas_' + id);
       sockets[id].send("<click args='" + (e.pageX - pc.offsetLeft) + "," + (canvii[id].clientHeight - (e.pageY - pc.offsetTop)) + "," + (e.button + 1) + "'>");
        // we need coords based on 0,0 in bottom left corner...
      } catch (err) {}
     }
    }

    var top_e = null;
    function clickCanvas(e,id,axes) {
     //alert("Clicked canvas for id " + id + " and axes " + axes);
     if (!e) var e = window.event;
        // e.button: 0 is left, 1 is middle, 2 is right.
     if ((e.button == 0) && (e.shiftKey == false) && (pan_mode == false)) {
      top_e = e;
      if (id > -1) zoom_canvas_id = id;
      var cnv = document.getElementById('plot_canvas_' + id);
      zdraw = axes;
      zdiv[id].style.width = 0;
      zdiv[id].style.height = 0;
      zdiv[id].style.top = (e.pageY - (cnv.offsetTop + cnv.offsetParent.offsetTop)) + "px";
      zdiv[id].style.left = (e.pageX - (cnv.offsetLeft + cnv.offsetParent.offsetLeft)) + "px";
      zdiv[id].style.display = "inline";
       // position the start of the zoom reticule
     }
     else {
      if (id > -1) pan_canvas_id = id;
      pdraw = axes;
      //zoomButtonDown = true;
     }
     startX = e.pageX;
     startY = e.pageY;
     pause = true;
     return false;
    }

    function clickMove(e,id) {
     move = id;
     mStartY = (e.pageY - document.getElementById('plot_canvas_' + id).offsetTop);
     mStartX = (e.pageX - document.getElementById('plot_canvas_' + id).offsetLeft);
     ztop += 1;
     document.getElementById('plot_canvas_' + id).style.setProperty('z-index',ztop);
    }

    function clickSize(e,id) {
     var cr = document.getElementById('resize_div');
     resize = id;
     rStartX = e.pageX;
     rStartY = e.pageY;
     document.getElementById('status_0').innerText = "Click size at " + rStartX + "," + rStartY;
     var pcs = document.getElementById('plot_canvas_' + id);
     cr.style.top = pcs.style.top;
     cr.style.left = pcs.style.left;
     cr.style.width = (pcs.clientWidth  - 2) + "px";
     cr.style.height = (pcs.clientHeight  - 4) + "px";
     cr.style.display = "inline";
     return false;
    }

    function slideSize(e) {
     if (resize > -1) {
      var cr = document.getElementById('resize_div');
      //resize_canvas(resize, (cw + (e.pageX - rStartX)), (ch + (e.pageY - rStartY)));
      cr.style.width = (e.pageX - cr.offsetLeft) + "px";
      cr.style.height = (e.pageY - cr.offsetTop) + "px";
      document.getElementById('status_0').innerText = "Slide size to " + (e.pageX - rStartX) + "," + (e.pageY - rStartY);
     }
     else if (move > -1) {
      var plc = document.getElementById('plot_canvas_' + move);
      plc.style.top = (e.pageY - mStartY) + "px";
      plc.style.left = (e.pageX - mStartX) + "px";
     }
     return false;
    }

    function do_resize(id, w, h) {
     if (id in sockets) {
      try {
       sockets[id].send("<resize args='" + w + "," + h + "'>");
      } catch (err) {}
     }
     else {
      var xScale = w / native_w[id];
      var yScale = h / native_h[id];
      resize_canvas(id, w, h);
       // no figure active for this canvas so do a purely client side resize
      allow_resize = false;
      canvii[id].width = canvii[id].width;
       // clear the canvas and reset scale factor before client size redraw
      document.getElementById('status_' + id).innerText = "Client side resize mode";
      contexts[id].scale(xScale, yScale);
       // needs to be done after resize_canvas, but this loses canvii[id].width/height so extra vars needed
      draw_frame(id);
       // the frame we draw may contain resize commands. Ignore these in client only mode hence the bracketing allow_resize directives.
      allow_resize = true;
     }
    }

    function outSize() {
     if (resize > -1) {
      var cr = document.getElementById('resize_div');
      do_resize(resize, cr.clientWidth, cr.clientHeight - 20);
      cr.style.display = "none";
     }
     resize = -1;
     move = -1;
     zdraw = -1;
     pdraw = -1;
      // make sure we kill everything on mouse up
    }

    function close_plot(id) {
     sockets[id].send("<close args=''>");
     stop_plotting(id);
     canvii[id].width = canvii[id].width;
    }

    function pan_toggle(id) {
     pan_mode = !pan_mode;
     if (!pan_mode) document.getElementById('pb').src = document.getElementById('button_pan').src;
     else document.getElementById('pb').src = document.getElementById('button_pan_over').src;
    }

    function go_home(id) {
     sockets[id].send("<home args=''>");
    }

    var zoom_canvas_id = 0;
    var pan_canvas_id = 0;

    function onDragOver(e) {
     if (e.preventDefault) e.preventDefault();
     this.className = 'over';
     e.dataTransfer.dropEffect = 'copy';
     return false;
    }

    function onDrop(e, id)
    {
     if (e.preventDefault) { e.preventDefault(); }
      // stop Firefox triggering a page change event
     top_e = e;
     var dt= e.dataTransfer;
     console.log(dt);
     var el_id = e.dataTransfer.getData('Text');
     stop_plotting(id);
     start_plotting(id, thumbnails.thumbnail_ports[el_id]);
     return false;
    }


    function conv_coords(id, pixelCoord, xdir) {
     var atop = 0;
     var aleft = 0;
     if (document.getElementById("anchor_div") != null) {
      an = document.getElementById("anchor_div");
      atop = an.offsetTop;
      aleft = an.offsetLeft;
     }
     var plc = document.getElementById("plot_canvas_" + id);
     if (xdir) {
      return pixelCoord - (plc.offsetLeft + aleft);
     } else {
      return canvii[id].height - (pixelCoord - (plc.offsetTop + atop));
     }
    } // convert from canvas pixels to mpl pixels

    function calc_coords(id, axes) {
     var mplStartX = conv_coords(id, startX, true);
     var mplStartY = conv_coords(id, startY, false);
     var mplStopX = conv_coords(id, stopX, true);
     var mplStopY = conv_coords(id, stopY, false);
     return axes + "," + mplStartX + "," + mplStopY + "," + mplStopX + "," + mplStartY;
    } // calculate the coordinates of the bounding box given by the canvas and the axes

    function do_pan(id, axes) {
     sockets[id].send("<pan args='" + calc_coords(id,axes) + "'>");
    }

    function zoom_in(id, axes) {
     sockets[id].send("<zoom args='" + calc_coords(id,axes) + "'>");
     startX=stopX=startY=stopY=0;
     zdiv[id].style.width="0px";
     zdiv[id].style.height="0px";
     zdiv[id].style.display = "none";
    }

    function releaseCanvas(e,id) {
     if (!e) var e = window.event;
     top_e = e;
     stopX = e.pageX;
     stopY = e.pageY;
     if (zdraw > -1 && ((stopX-startX)>5) && ((stopY-startY)>5)) { zoom_in(zoom_canvas_id, zdraw);}
     else if (zdraw == -1 && (Math.abs(stopX-startX)>5) || (Math.abs(stopY-startY)>5)) {
      do_pan(pan_canvas_id, pdraw);
     }
     else {
      // not in zdraw (or zoomed areas less than 5x5) so normal click
      handle_click(e,id);
      zdiv[id].style.display = "none";
     }
     zdraw = -1;
     pdraw = -1;
     pause = false;
     return false;
    }

    function slideCanvas(e,id,axes) {
     if (!e) var e = window.event;
     if (zdraw > -1)  {
      zdiv[id].style.width = e.pageX - startX + "px";
      zdiv[id].style.height = e.pageY - startY + "px";
     }
     if (cursor_info[id] == 0) {
       var dataX = Number.NaN;
       var dataY = Number.NaN;
       for (var i=0; i < ax_bb.length; i++) {
         ax_width = ax_bb[i][4] - ax_bb[i][0];
         ax_height = ax_bb[i][3] - ax_bb[i][1];
         if ((ax_width == 0.0) || (ax_height == 0.0)) {
           continue;
         }
         var pixX = conv_coords(id, e.pageX, true);
         var pixY = conv_coords(id, e.pageY, false);
         var relX = (pixX - ax_bb[i][0] - canvii[id].offsetLeft) / ax_width;
         var relY = (pixY - ax_bb[i][1] - canvii[id].offsetTop) / ax_height;
         // Remember that HTML y increases from top to bottom while data ylim goes other way
         if ((relX >= 0.0) && (relX <= 1.0) && (relY >= 0.0) && (relY <= 1.0)) {
           // Check if cursor is above current axes (this should be true anyway due to div!)
           data_width = ax_datalim[i][1] - ax_datalim[i][0];
           data_height = ax_datalim[i][3] - ax_datalim[i][2];
           dataX = relX * data_width + ax_datalim[i][0];
           dataY = relY * data_height + ax_datalim[i][2];
           break;
         } else {
           dataX = Number.NaN;
           dataY = Number.NaN;
         }
       }
       var cursor_str = "";
       if (!isNaN(dataX) && !isNaN(dataY)) {
         cursor_str = "Cursor:  " + dataX.toString().substr(0, 6) + ", " + dataY.toString().substr(0, 6);
       }
       document.getElementById('cursor_info_' + id).innerText = cursor_str;
     }
     return false;
    }
    document.captureEvents(Event.MOUSEMOVE)
    document.onmousemove = slideSize;
</script>
</body>
</html>
"""
