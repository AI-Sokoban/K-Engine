لعبة sokoban حلالا
==============================
يقدم هذا المشروع حلاً للذكاء الاصطناعي لـ sokoban (اليابانية لأمين المستودعات) ، وهي مشكلة حسابية صعبة. تتضمن الخوارزميات المستخدمة BFS (بحث واسع) و DFS (بحث عميق أولًا) و UCS (بحث تكلفة موحد) و A * (بحث نجمة).

## قائمة المحتويات

* [0. كيف تستعمل] (# 0)
* [1. نظرة عامة] (رقم 1)
* [2. مقارنة النتائج] (رقم 2)

<a id="0"> </a>
## 0. كيفية الاستخدام

1. المكتبات التي سيتم استيرادها هي: "sys" ، "المجموعات" ، "numpy" ، "heapq" ، "time".

2. بعد التنزيل في الجهاز قم بتشغيل ملف `sokoban.py`.

### عرض مساعده

""
$ python sokoban.py - help
""
""
الاستخدام: sokoban.py [خيارات]

خيار:
  -h، - help إظهار رسالة المساعدة هذه والخروج.
  -l SOKOBANLEVELS ، - المستوى = SOKOBANLEVELS
                        مستوى اللعبة للعب (test1-10.txt ، المستوى1-5.txt)
  -m طريقة الوكيل ، - الطريقة = طريقة الوكيل
                        طرق البحث (bfs ، dfs ، ucs ، astar)
""

"-l": الخريطة مقسمة إلى اختبارات ومستويات. الاختبار بسيط للغاية. ومستويات أكثر صعوبة
"-m": خوارزمية البحث هي bfs أو dfs أو ucs أو astar.

### قم بتشغيل المثال

""
$ python sokoban.py -l test1.txt -m bfs
""
""
rUdRdrUluL
وقت تشغيل bfs: 0.15 ثانية
""
نتيجة السطر الأول هي عمل أداة الضغط `u`` d` `l`` r` التي تمثل التحرك لأعلى ولأسفل ولليسار ولليمين على التوالي. ويمثل الحرف الكبير المقابل دفع الصندوق. اذهب في هذا الاتجاه يعرض السطر الثاني وقت تنفيذ البرنامج.

<a id="1"> </a>
## 1. نظرة عامة

سوكوبان ، المعروف أيضًا باسم سوكوبان [رابط اللعبة] (https://www.mathsisfun.com/games/sokoban.html) ، يتعين على اللاعبين دفع كل الصناديق إلى وجهتهم لتحقيق النجاح.

### خريطة عينة ("level1.txt")

**شكل صورة:**

! [] (./ img / level1.png)

** استمارة الإدخال: **

""
  #####
### #
#.&ب #
###ب.#
#.##ب #
# #. ##
# BXBB #
#. #
##########
""

حيث "#" جدار ، "." وجهة ، "B" مربع ("X" مربع في الوجهة) ، "&" الشخص الذي يدفع الصندوق ("٪" هو المربع على الوجهة). المساحة هي المنطقة التي يمكن نقلها. ويمكن نقلها

### أفكار

فهم بسيط فيما يتعلق باستخدام خوارزميات البحث هنا في الوضع الحالي يتخذ الدافع جميع الإجراءات الممكنة لإنشاء الحالة التالية ، وما إلى ذلك ، حتى تكون الحالة الأخيرة هي الحالة النهائية. لأنه يتم استخدام خوارزميات البحث. أول شيء يجب تحديده هو الرسم البياني لمساحة الحالة (SSG) وشجرة البحث (ST). إذا تم تخزين جميع خرائط الإدخال مباشرة كمجموعات SSG في بنية البيانات يزداد استخدام الذاكرة مع تقدم البحث ، لذلك يجب إعادة تعيين SSG الجديد. الأمر الذي لا يقلل فقط من احتلال الفضاء لكنه يظهر أيضًا معلومات كافية.في مشاكل سوكوبان ، يكون الجوهر هو موقع الصندوق وموقع الشخص. نظرًا لأن موقع الجدار والوجهة متماثلان ، يكون شكل تعريف SSG كما يلي. حيث يمثل الصف الأول إحداثيات الشخص الحالي. وتمثل المجموعة الثانية إحداثيات المربع الحالي.

""
((2 ، 2) ، ((2 ، 3) ، (3 ، 4) ، (4 ، 4) ، (6 ، 1) ، (6 ، 4) ، (6 ، 5)))
""

ST هو فرع من SSG الحالي بناءً على الإجراءات الممكنة للدافع ، كل إجراء يؤدي إلى إنشاء SSG جديد ومختلف. وفي النهاية سيتم إنشاء المزيد من الفروع والعقد. طالما أن إحداثيات جميع المربعات وإحداثيات الوجهة متطابقة تمامًا ، تنتهي اللعبة (النصر). ولكن في ألعاب sokoban ، غالبًا ما يتم دفع الصناديق إلى بعض المواضع ، مثل طريق مسدود. يؤدي هذا الموقف إلى نهاية اللعبة (فشل) في الواقع ، لذلك ليست هناك حاجة للاستمرار ، لذا فإن استخدام هذه الأنماط التي تؤدي إلى طريق مسدود يمكن أن يساعدنا في قطع الشجرة. لذلك ، يتم تقليل عدد العقد المنفصلة بشكل كبير. هذا يقلل من أثر الذاكرة. يوضح الشكل التالي نمطًا ثابتًا. مع صندوق في المنتصف إذا ظهرت هذه المواقف في الدائرة المحيطة ، فإن الحالة الحالية لم تعد بحاجة إلى الفصل.

! [] (./ img / dead_patterns.jpg)

بالإضافة إلى ذلك ، لمنع الدافع من القيام بحركات لا معنى لها مثل التأرجح ذهابًا وإيابًا دون الضغط على الصندوق. نحتاج إلى إنشاء SSG بعد أن لا يكرر كل فرع SSG على نفس الفرع ، أي لا يمكن تكرار موقع a. "الأشخاص وجميع الحقول" "الموقع"

ثم هناك جزء من خوارزميات BFS و DFS الذي لن يقول الكثير. "طريق واحد إلى الموت والآخر." تمت إضافة دالة التكلفة إلى UCS ، وهي "اتخاذ أكثر الطرق فعالية من حيث التكلفة". تُعرَّف دالة التكلفة هنا على أنها: عدد الخطوات التي تم اتخاذها دون الاحتفاظ بالمربع في الوضع الحالي هذا يحفز الدافعين للقيام بأكبر عدد ممكن من الحركات ذات المغزى. بدلا من التجول بدون الضغط على المربع الأخير A * إضافة دالة إرشادية إلى دالة التكلفة والغرض من ذلك هو تشجيع المندفعين ليس فقط على دفع الصندوق. ولكن أيضًا لدفع الصندوق إلى وجهته. تستخدم الدالة الاستكشافية هنا مسافة مانهاتن. هذا يعني مجموع مسافات مانهاتن بين جميع مواضع تسلسل الصندوق وجميع مواضع تسلسل الوجهة إلى الحالة الحالية.

<a id="2"> </a>
## 2. مقارنة النتائج

* BFS:

""
$ python sokoban.py -l test1.txt -m bfs
rUdRdrUluL
وقت تشغيل bfs: 0.15 ثانية

$ python sokoban.py -l test1.txt -m bfs
rUdRdrUluL
وقت تشغيل bfs: 0.13 ثانية

$ python sokoban.py -l test2.txt -m bfs
UddrrrUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUU
وقت تشغيل bfs: 0.01 ثانية

$ python sokoban.py -l test3.txt -m bfs
LrdrddDLdllUdR
وقت تشغيل bfs: 0.27 ثانية

$ python sokoban.py -l test4.txt -m bfs
llldRRR
وقت تشغيل bfs: 0.01 ثانية

test5.txt: أكثر من دقيقة واحدة

$ python sokoban.py -l test6.txt -m ب
خ
dlluRdrUUddrruulL
وقت تشغيل bfs: 0.02 ثانية

$ python sokoban.py -l test7.txt -m bfs
LUUUluRddddLdlUUUUluR
وقت تشغيل bfs: 1.25 ثانية

$ python sokoban.py -l test8.txt -m bfs
llDDDDDDldddrruuLuuuuuurrdLulDDDDDDlllddrrUdlluurRdddrruuLUUUUUUluRddddddddddrddlluUdlluurRdrUUUUUU
وقت تشغيل bfs: 0.30 ثانية

$ python sokoban.py -l level1.txt -m bfs
RurrddddlDRuuuuLLLrdRDrddlLdllUdR
وقت تشغيل bfs: 35.04 ثانية.
""

* DFS:

""
$ python sokoban.py -l test1.txt -m dfs
rrUrdllluRRlldrrrUlllururrDLrullldRldrrUruLrdllldrrdrUlllurrurDluLrrdllldrrdrU
وقت تشغيل dfs: 0.09 ثانية

$ python sokoban.py -l test2.txt -m dfs
Grrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr
وقت تشغيل dfs: 0.01 ثانية.

$ python sokoban.py -l test3.txt -m dfs
rrdldrdllDRlldlUrrrdrruLrdllLrrrululldRllldRlurrrdrruLrdllUrrdllLrrrullllldRRRlllurrrrrdLrulllllUdrrrrrdlLrrullllldrRRlllurrrrrdLrullluRldrrrdlLrrullllldrRRlllurrrrrdLrulllururulluLrrrdlddldrrrdlLrrullllldrRRlllurrrrrdLrulUlldrrrdlLrrullllldrRRlllurrrrrdLrulllurrUldrdrdlLrrullllldrRRlllurrrrrdLrulllurrululurrDDldldrrrdlLrrulllururDlldrdrruLrdllLrrrululldRllldRlurrrdLrrruLrdlllulldRRRlllurrurrdrdLrulL
وقت تشغيل dfs: 0.36 ثانية

$ python sokoban.py -l test4.txt -m dfs
غررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررررر
وقت تشغيل dfs: 0.01 ثانية.

test5.txt: أكثر من دقيقة واحدة

$ python sokoban.py -l test6.txt -m dfs
greesssssssssssssssssssssssssssssssssssssssssssssss
وقت تشغيل dfs: 0.02 ثانية

$ python sokoban.py -l test7.txt -m dfs
rdllllurRlldrrrruulLrrdLrdllllurRlldrrrruullLrrrdLrdllllurRlldrrrruulluulldDrrrrdLrdllllUrdrrrulLrrdlllluUrrrrdllLrrrullllUdrrrrdllldlUrrrrulluululldRRllurrrrrdddllldrrrdlllluUrrrruuullllldrDDrrrrdllldlUrrrrulluUlllurrRllldrrrddrrdllllUrrrruuuLrdddllllUdrruuluRllldRRllurrrDllddrrrruuuLrdddlllluurrDDrrdlLrrdlllluRRlldrrrruulllluuruRllldrrrddrrdLrdllllurRlldrrrruuuuuLrdddlllldrrdrUrdllllurrulluuruRllldrrrddlldrrrruLrdllllurRlldrrrruuuuLrdddLrdlllluuuruRllldrrrdDrruuuLrdddlllluu
ruRllldrrrddrrdlLrrdlllluurrrruuLrdddllllddrrrrullLrrrrllllUrrrrulluul
وقت تشغيل dfs: 0.78 ثانية.

$ python sokoban.py -l test8.txt -m dfs
llDlurrrdLrullldRDDDDDlllddrrdrruuLrddllulluurrruuuuulurrrdLrullldRdddddlllddrrUruLruuuuulurrrdLrullDDDDDDlddlluuRRllddrrdrruuLrddllulluurrDrUldrrddllUlluurrrUdlllddrrUruLruUddldrrddllulluuRlddrrdrruuluLruuUdddldrrddllulluuRlddrrdrruuluLruuuUddddldrrddllulluuRlddrrdrruuluLruuuuUluRldrdddddldrrddllulluuRRllddrrdrruulUUUUUU
وقت تشغيل dfs: 0.11 ثانية.

level1.txt: أكثر من دقيقة واحدة
""

* UCS:

""
$ python sokoban.py -l test1.txt -m ucs
rURdrUlLdlU
وقت تشغيل ucs: 0.09 ثانية

$ python sokoban.py -l test2.txt -m ucs
UUdrrrrUU
وقت تشغيل ucs: 0.01 ثانية

$ python sokoban.py -l test3.txt -m ucs
LrdrddDLdllUdR
وقت تشغيل ucs: 0.17 ثانية

$ python sokoban.py -l test4.txt -m ucs
llldRRR
وقت تشغيل ucs: 0.01 ثانية

test5.txt: أكثر من دقيقة واحدة

$ python sokoban.py -l test6.txt -m ucs
dlluRdrUUddrruulL
وقت تشغيل ucs: 0.02 ثانية

$ python sokoban.py -l test7.txt -m ucs
LUUUluRddddLdlUUUUluR
وقت تشغيل ucs: 0.94 ثانية

$ python sokoban.py -l test8.txt -m ucs
llDDDDDDldddrruulululuhululuDDDDDDlllddrrUdlluurRdddrruuLUUUUUUluRddddddrlluUdlluurRdrUUUUUU
وقت تشغيل ucs: 0.31 ثانية

$ python sokoban.py -l level1.txt -m ucs
RurrddddlDRuuuuLLLrdRDrddlLdllUdR
وقت تشغيل ucs: 33.22 ثانية
""

* النجوم

""
$ python sokoban.py -l test1.txt -m astar
rUdRdrUluL
وقت تشغيل ممتاز: 0.01 ثانية.

$ python sokoban.py -l test2.txt -m astar
UUdrrrrUU
وقت تشغيل ممتاز: 0.01 ثانية.

$ python sokoban.py -l test3.txt -m astar
LrdrddDLdllUdR
وقت تشغيل ممتاز: 0.01 ثانية.

$ python sokoban.py -l test4.txt -m astar
llldRRR
وقت تشغيل نجم: 0.00 ثانية

$ python sokoban.py -l test5.txt -m astar
uruLdlUURUdRdrUllLdlU
وقت تشغيل نجم: 0.11 ثانية

$ python sokoban.py -l test6.txt -m astar
dlluRdrUUddrruulL
وقت تشغيل نجم: 0.02 ثانية

$ python sokoban.py -l test7.txt -m astar
LUUUluRddddLdlUUUUluR
وقت تشغيل نجم: 0.16 ثانية

$ python sokoban.py -l test8.txt -m astar
llDDDDDDldddrruulululuhululuDDDDDDlllddrrUdlluurRdddrruuLUUUUUUluRddddddrlluUdlluurRdrUUUUUU
وقت تشغيل ممتاز: 0.33 ثانية

$ python sokoban.py -l level1.txt -m astar
RurrdLLLRrrdddlDRlLdllUdRRurruuulldRDrddL
وقت تشغيل نجم: 0.85 ثانية
""

أفضل أداء هو دافع صندوق الإخراج A * ، حيث تتحرك BFS و UCS و A * بنفس الطريقة ، على الرغم من أن DFS يمكن أن تجد مخرجًا أيضًا. لكن هذه الظاهرة ستحدث ، بالطبع ، طرق أخرى ستجعل النتيجة أسهل. تشمل المجالات التي يمكن تحسينها في المستقبل ما يلي:

* تحديد أبسط SSG.
* تنسيقات يموت أكثر شمولاً
* وظائف تكلفة ووظائف إرشادية أكثر ملاءمة.