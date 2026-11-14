# 📖 patch 77 (dashboard v3.36.46 · the tutorial button) — the owner (14-11): «اريد كل بوت فيه زر تعليم يوضح كيف شغل البوت بالتفصيل
#   اجزاء مقتطعه ومثال متحرك وشرح واساله واجوبه بالاخير لعمل الابوات كليا وكذلك شرح على ازرار الكرت».
#   «📖» on every bot card (next to ⚙ — every card kind) opens one window (showModal · rule 14) for that bot's kind:
#   💡 the idea · 🧩 step by step · 🎬 a moving example (the price · the levels · the trades as they happen · the profit — drawn for
#   that kind: ♾️ ➕ 🎚️ 🪜 📈 📉 🔁 🔂 💹) · 🔘 the card's buttons (the very buttons of that card) · 🧾 the card's numbers ·
#   ❓ questions and answers (that bot, then all bots). MSA · the theme's colours only (rule 15) · nothing is sent anywhere.
#   python3 devtests/step/patches/p77_tutorial.py Holy_Dashboard.pyw
import os, sys

JS = r'''/* 📖 v3.36.46: زر «تعليم» بكل بطاقة — كيف يعمل البوت بالتفصيل: الفكرة · خطوة بخطوة · مثال متحرك · أزرار البطاقة · أرقامها · أسئلة وأجوبة */
const TUT_BTN={
  pw:['⏹ / ▶️','إيقاف البوت أو تشغيله. الإيقاف لا يلغي أوامره على المنصة ولا يمسح حسابه — حين يعود يكمل من حيث توقف.'],
  ab:['⏸ إيقاف الشراء','لا شراء من سعر السوق الآن (أو من سعر تكتبه). كل مستوى ينزل إليه السعر يُحفظ ويُعدّ على البطاقة («▶️ استئناف الشراء (N)»)، وعند الاستئناف تُشترى كلها مرة واحدة بسعر السوق — أرخص من مستوياتها — وتعود بيعاتها إلى أماكنها.'],
  as:['⏸ إيقاف البيع','العكس: لا بيع من هذا السعر صعوداً. كل مستوى يتجاوزه السعر يُحفظ، وعند الاستئناف يُباع مرة واحدة بسعر السوق — أغلى من مستوياته.'],
  chart:['📈 شارت','رسم السعر الحي داخل البطاقة نفسها، مع خطوط أوامر البوت.'],
  lddr:['🪜 السلم','كل درجات البوت في نافذة واحدة: الحية على المنصة والتي في ذاكرته، بأسعارها وكمياتها، وأين السعر الآن.'],
  rilad:['💠 سلّم الإعادة','يظهر مع إعادة الاستثمار: كم كبر أمر كل درجة من أرباحها.'],
  hist:['📜 السجل','كل ما فعله البوت بالترتيب: الشراءات والبيعات وربح كل بيعة، والإيقاف والاستئناف والتنبيهات.'],
  cset:['⚙','تفاصيل البوت: إعداداته وتعديلها · المحفظة المرتبطة · نسخ الإعدادات لبوت جديد · معلومات التشغيل.'],
  del:['🗑','حذف نهائي: يلغي البوت أوامره هو على المنصة ويتأكد من إلغاء كل أمر، ثم يُحذف (يبقى سجله في 🗄️ الأرشيف). العملات والدولار يبقيان في محفظتك.'],
  ri:['🔄 إعادة الاستثمار','تشغيل أو إيقاف إعادة الاستثمار: نسبة من ربح كل دورة تعود إلى أمر الدرجة نفسها فيكبر. عند الإيقاف يتحرر ما أُعيد استثماره ويُحسب ربحاً.'],
  guard:['⚔️ درع السكين','حماية من الانهيار السريع: إن هبط السعر بقوة في وقت قصير يوقف الشراء تلقائياً ويحفظ الدرجات حتى يهدأ السوق.'],
  table:['📋 الجدول','ماذا سيفعل البوت عند كل سعر — قبل أن يحدث — ويتحدّث مع التشغيل.'],
  dca_close:['💰 أغلق الدورة الآن','يغلق الدورة الحالية فوراً بسعر السوق: في الشرائي يبيع الكمية كلها، وفي البيعي يعيد شراءها (قد يكون بخسارة إن لم يصل السعر إلى الهدف).'],
  dca_trail:['🛡️ الدرع','التتبّع: حين يعبر السعر مستوى أمان لا ينفّذ فوراً، بل يلاحق القاع (أو القمة في البيعي) وينفّذ عند الارتداد بالنسبة المحددة — سعر أفضل في الهبوط الطويل.'],
  dca_last:['🏁 آخر دورة ويخرج','يكمل الدورة الحالية حتى تُغلق بربحها، ثم يتوقف ولا يبدأ دورة جديدة.'],
  dca_pause:['⏸ إيقاف','يوقف البوت مؤقتاً — أوامره ودورته تبقى كما هي.'],
  rngb:['✏️','تعديل نطاق السعر الذي يشتري (أو يبيع) داخله — خارج النطاق يتخطّى الموعد.'],
  rip:['⚖️','نسبة ربح كل صفقة التي تعود فتُضاف إلى الأمر القادم (إعادة استثمار الدوري).'],
  riw:['💸','يحرّر الربح المعاد استثماره ويعيده ربحاً محقّقاً.'],
  sellall:['💰 الكل الآن','يغلق كل الأوامر المفتوحة الآن بسعر السوق (في الشرائي بيعاً وفي البيعي إعادة شراء) — قد يكون بعضها بخسارة.'],
  now_rec:['🛒 / 🏷️ الآن','صفقة فورية خارج الموعد بالمبلغ نفسه.'],
  pause_rec:['⏸ أوقف','يتوقف التنفيذ الدوري، وتبقى الأوامر المفتوحة تعمل حتى تبلغ أهدافها.'],
  va_now:['⏩ خطوة الآن','ينفّذ خطوة المسار الآن (يقارن القيمة بالهدف فيشتري أو يبيع الفرق) بدل انتظار موعدها.'],
  va_set:['⚙️ الإعدادات','تعديل مبلغ الخطوة والهامش وأكبر أمر والميزانية والمكابح والحماية — يطبّقها المحرك حياً.'],
  va_exit:['✋ بيع الكل','يبيع كل ما يحمله البوت بسعر السوق ويخرج من المسار.']
};
const TUT_NUM=[['الرقم الكبير','الربح المحقق من صفقات أُغلقت (بعد العمولة) — لا ينقص حين ينزل السعر.'],['اليوم','ما تحقق اليوم.'],['السعر','سعر العملة الآن، والسهم اتجاهه.'],
  ['🔺 أدنى بيع · 🔻 أعلى شراء','أقرب أمرين للسعر من الجهتين.'],['💰 رصيدك','العملة والدولار الحرّان في المحفظة.'],['💵 تحتاج','الدولار الذي تحتاجه الدرجات المحفوظة في الذاكرة لو نزل السعر إليها.'],
  ['📡 أوامر المنصة','عدد أوامر البوت الحية على المنصة.'],['⏱️ التشغيل','منذ متى يعمل.'],['📈 المعدل','ربحه اليومي والشهري والسنوي المتوقع من تداوله هو.']];
const TUT={
  grid:{a:'grid',t:'الشبكة اللانهائية',
    idea:['يقسم بوت الشبكة السعر إلى درجات متساوية النسبة (مثلاً 0.6%): تحت السعر أوامر شراء، وفوقه أوامر بيع. كلما نزل السعر درجة اشترى، وكلما صعد درجة باع ما اشتراه بربح الدرجة.',
          'سُمّيت «لانهائية» لأنها بلا سقف: تبيع من عملاتك فوق سعر البداية وتتبع السعر صعوداً ونزولاً، ولا تشتري تحت «أدنى سعر» الذي تحدده.'],
    steps:[['السلّم','ينطلق من سعر البداية (أو سعر السوق) ويرسم درجات بنسبة الشبكة فوقه وتحته.'],
           ['الأوامر الحية','أقرب 4 أوامر شراء و4 أوامر بيع على المنصة، والباقي في ذاكرة البوت ينزل إلى المنصة حين يقترب السعر.'],
           ['الشراء','ينزل السعر إلى درجة ⇐ يُنفَّذ الشراء ⇐ يضع البوت فوراً أمر بيع للكمية نفسها على الدرجة التي فوقها.'],
           ['البيع','يصعد السعر إلى ذلك البيع ⇐ يُنفَّذ ⇐ ربح الدورة (نسبة الشبكة ناقص العمولة) ⇐ يعود أمر الشراء إلى مكانه.'],
           ['التكرار','كل نزول وصعود داخل السلّم دورة ربح جديدة — التذبذب هو مصدر الربح.'],
           ['الحماية','«أدنى سعر» يمنع الشراء تحته · ⚔️ درع السكين يوقف الشراء عند الانهيار السريع · ⏸ إيقاف الشراء والبيع من سعر تختاره.']],
    btns:['pw','ab','as','chart','lddr','rilad','hist','cset','del','ri','guard'],
    faq:[['ماذا لو نزل السعر كثيراً؟','يشتري درجة بعد درجة حتى ينفد الدولار أو يصل إلى «أدنى سعر». تنتظر العملات المشتراة صعود السعر لتُباع كل منها بربح درجتها. النقص في قيمتها على الورق فقط حتى يعود السعر.'],
         ['ماذا لو صعد السعر بقوة؟','يبيع درجة بعد درجة من عملاتك. إن نفدت العملات فوق السعر توقف البيع حتى يعود السعر إلى السلّم.'],
         ['ما نسبة الشبكة المناسبة؟','أكبر من ضعف العمولة (نحو 0.2%). النسبة الصغيرة: دورات كثيرة وربح قليل لكل دورة · الكبيرة: العكس.'],
         ['ما إعادة الاستثمار 💠؟','نسبة من ربح كل دورة تعود إلى أمر الدرجة نفسها فيكبر مع الوقت، بدل أن تُحسب ربحاً محرَّراً.']]},
  grid_plus:{a:'plus',t:'بلس',
    idea:['مثل الشبكة تماماً، لكن شراء كل بيعة يُفتح أبعد تحتها بمسافة تختارها (بُعد الشراء — مثلاً 1.2%)، فيصير ربح كل دورة بحجم هذا البُعد بدل درجة واحدة.',
          'مناسب للعملات التي تتذبذب بقوة: دورات أقل، وكل دورة تربح أكثر.'],
    steps:[['السلّم','الدرجات نفسها بنسبة الشبكة.'],['الفجوة','بُعد الشراء يُقرَّب إلى عدد صحيح من الدرجات (1.2% مع شبكة 0.6% = درجتان) حتى تبقى الدورة مغلقة.'],
           ['الشراء','يُنفَّذ شراء على درجة ⇐ يوضع بيعه فوقه بعدد درجات الفجوة.'],['البيع','يُنفَّذ البيع ⇐ يعود شراؤه تحته بالفجوة نفسها.'],
           ['الباقي','الحماية والإيقاف وإعادة الاستثمار كما في الشبكة.']],
    btns:['pw','ab','as','chart','lddr','rilad','hist','cset','del','ri','guard'],
    faq:[['ما الفرق بين البلس والشبكة؟','في الشبكة الشراء والبيع متجاوران (درجة واحدة)؛ في البلس بينهما فجوة — ربح أكبر لكل دورة ودورات أقل.'],
         ['لماذا لا يشتري على كل درجة تحت البيع؟','لأن مكان شراء كل بيعة محجوز على مسافة الفجوة؛ هذا ما يجعل كل دورة تربح البُعد كاملاً.']]},
  grid_range:{a:'range',t:'المدى',
    idea:['شبكة محصورة بين حدين تختارهما. يرسم السلّم كله بين الحدين من البداية، ولا يتمدّد خارجهما.',
          'لا شراء تحت الحد الأدنى ولا بيع فوق الحد الأعلى — مناسب حين تتوقع أن يتحرك السعر داخل مدى معروف.'],
    steps:[['السلّم الثابت','درجات بنسبة الشبكة بين الحدين: شراءات تحت السعر وبيعات (من عملاتك) فوقه.'],['داخل المدى','دورة الشبكة نفسها: شراء ثم بيع على الدرجة التي فوقه.'],
           ['تحت الحد الأدنى','يتوقف الشراء وتنتظر الدرجات عودة السعر.'],['فوق الحد الأعلى','تكون العملات قد بيعت كلها، فيبقى الدولار حتى يعود السعر.']],
    btns:['pw','ab','as','chart','lddr','rilad','hist','cset','del','ri','guard'],
    faq:[['كم عملة يحتاج؟','بقدر البيعات من سعر البداية إلى الحد الأعلى؛ نموذج النشر يحسبها قبل التشغيل.'],
         ['ماذا لو بقي السعر خارج المدى طويلاً؟','لا يخسر صفقات لكنه لا يتداول حتى يعود السعر، ويمكنك تعديل الحدين من ⚙.']]},
  grid_step:{a:'step',t:'المتدرج',
    idea:['شبكة متدرجة: كل مستوى شراء يُقسم إلى أجزاء، وكل جزء يبيع على مسافة مختلفة فوق شرائه — الأول قريب والأخير أبعد.',
          'فيأخذ ربحاً سريعاً من الحركة الصغيرة، ويترك جزءاً يلحق الصعود الكبير.'],
    steps:[['المستويات','بنسبة الشبكة، وقيمة كل مستوى مقسومة على عدد الأجزاء.'],['الشراء','ينزل السعر إلى مستوى ⇐ تُشترى أجزاؤه.'],
           ['البيعات المتدرجة','الجزء الأول على «مسافة البيع الأولى»، ثم كل جزء أبعد بمقدار «مسافة البيع».'],['الدورة','كل جزء يُباع ⇐ يعود شراؤه إلى مستواه ليتكرر.'],
           ['النافذة','على المنصة أقرب عدد محدد من الأوامر في كل جهة، والباقي في ذاكرة البوت.'],
           ['الإيقاف','⏸ لا شراء تحت الأرضية · عند الاستئناف يُشترى ما تجاوزه السعر فوراً بسعر السوق (أرخص من مستواه) — والعدّاد على البطاقة يعرض كم.']],
    btns:['pw','ab','as','chart','lddr','hist','cset','del','ri'],
    faq:[['لماذا الأجزاء؟','الحركة الصغيرة متكررة والكبيرة نادرة: الجزء القريب يربح مرات كثيرة، والبعيد يربح أكثر حين يأتي الصعود.'],
         ['هل يعمل بإعادة الاستثمار؟','نعم — لكل جزء حصّالته: ربح بيعه يكبّر شراءه القادم.'],
         ['هل أشغّل أكثر من متدرج على العملة؟','لا — بوت متدرج واحد لكل عملة حتى لا تتداخل أجزاؤه.']]},
  dca_buy:{a:'dcab',t:'DCA الشرائي',
    idea:['يشتري أمراً أولياً، ثم يشتري أكثر كلما نزل السعر (أوامر أمان أكبر فأكبر) فينخفض متوسط كلفته. حين يرتفع السعر فوق المتوسط بنسبة الهدف يبيع الكل بربح — الربح بالدولار.',
          'دورة بعد دورة: تُغلق الدورة ثم تبدأ أخرى بعد مهلة.'],
    steps:[['الأمر الأولي','شراء بسعر السوق.'],['أوامر الأمان','مستويات تحت السعر: الانحراف يتسع (مضاعف الخطوة) والحجم يكبر (مضاعف الحجم).'],
           ['المتوسط','كل أمر أمان يُنفَّذ ⇐ ينخفض المتوسط ⇐ ينخفض الهدف.'],['الإغلاق','الهدف = المتوسط + نسبة الربح ⇐ يبيع الكمية كلها وتُغلق الدورة.'],
           ['🛡️ التتبّع','بدل التنفيذ عند المستوى يلاحق القاع وينفّذ عند الارتداد.']],
    btns:['dca_close','dca_trail','dca_last','hist','table','lddr','chart','dca_pause','cset','del'],
    faq:[['ماذا لو نفدت أوامر الأمان والسعر ينزل؟','ينتظر عودة السعر إلى الهدف؛ لا يبيع بخسارة إلا إن أغلقت الدورة بنفسك (💰).'],
         ['لماذا يكبر حجم أوامر الأمان؟','حتى ينخفض المتوسط بسرعة فيقترب الهدف من السعر.']]},
  dca:{a:'dcas',t:'DCA البيعي',
    idea:['العكس: يبيع جزءاً من عملتك، ويبيع أكثر كلما صعد السعر فيرتفع متوسط سعر البيع. حين ينزل السعر تحت المتوسط بنسبة الهدف يعيد الشراء بكمية أكبر مما باع — الربح بالعملة.',
          'مناسب لمن يحمل العملة ويريد أن يزيد عددها من صعود السعر وهبوطه.'],
    steps:[['البيع الأولي','بيع بسعر السوق.'],['أوامر الأمان','مستويات فوق السعر تتسع ويكبر حجمها.'],['المتوسط','كل بيع يُنفَّذ ⇐ يرتفع متوسط البيع.'],
           ['الإغلاق','ينزل السعر إلى المتوسط ناقص نسبة الربح ⇐ يعيد شراء كل ما باع بدولاره ⇐ عملات أكثر.']],
    btns:['dca_close','dca_trail','dca_last','hist','table','lddr','chart','dca_pause','cset','del'],
    faq:[['لماذا الربح بالعملة؟','لأنه يبيع غالياً ويشتري رخيصاً بالدولار نفسه، فيعود بعملات أكثر مما باع.']]},
  rec_buy:{a:'recb',t:'الشراء الدوري',
    idea:['يشتري مبلغاً ثابتاً كل مدة (ساعة · يوم · أسبوع) مهما كان السعر — يوزّع الدخول على الزمن. ولكل شراء هدف ربح يُباع عنده.'],
    steps:[['الموعد','كل مدة يشتري المبلغ بسعر السوق.'],['الأوامر','«أوامر منفصلة»: كل شراء يُباع وحده عند +نسبة الهدف · «المتوسط»: تُباع الكمية كلها عند المتوسط + نسبة الهدف.'],
           ['النطاق','اختياري: لا شراء خارج حدين سعريين.'],['حد الأمان','أقصى مبلغ مفتوح؛ إن امتلأ يتخطّى الشراء حتى يُباع أمر.'],['⚖️ إعادة الاستثمار','نسبة من ربح كل صفقة تُضاف إلى الأمر القادم.']],
    btns:['rngb','rip','riw','sellall','now_rec','pause_rec','hist','chart','pw','cset','del'],
    faq:[['ماذا لو لم يكفِ الدولار في الموعد؟','يتخطّى الموعد ويكمل في القادم — رسالة واحدة ثم صمت حتى يمر شراء.'],['هل يشتري في القمة؟','نعم أحياناً — لكنه يشتري في القاع أيضاً، فيتقارب المتوسط مع الزمن.']]},
  rec_sell:{a:'recs',t:'البيع الدوري',
    idea:['يبيع مبلغاً ثابتاً من عملتك كل مدة، ويعيد شراء كل بيعة حين ينزل السعر بنسبة الهدف — فتعود بعملات أكثر.'],
    steps:[['الموعد','كل مدة يبيع المبلغ بسعر السوق.'],['إعادة الشراء','كل بيعة لها هدف تحت سعرها بنسبة الربح.'],['حد الأمان','أقصى ما يكون مبيعاً بانتظار إعادة الشراء.']],
    btns:['rngb','rip','riw','sellall','now_rec','pause_rec','hist','chart','pw','cset','del'],
    faq:[['ماذا لو صعد السعر ولم يعد؟','تبقى البيعات بانتظار هدفها؛ ربحك بالدولار من البيع موجود، لكن العملات لم تعد بعد.']]},
  rec_va:{a:'va',t:'مسار القيمة',
    idea:['يحدد هدفاً لقيمة العملة التي يحملها البوت يكبر بمبلغ ثابت كل خطوة. إن كانت القيمة أقل من الهدف يشتري الفرق، وإن كانت أكثر يبيع الزائد.',
          'فيشتري أكثر حين ينزل السعر ويبيع حين يصعد — تلقائياً.'],
    steps:[['الهدف','يبدأ بمبلغ البداية ويزيد بمبلغ الخطوة كل مدة (أو كل نسبة سعر في نمط «بالنسبة»).'],['المقارنة','قيمة العملة المحمولة = الكمية × السعر.'],
           ['أقل من الهدف','شراء الفرق (حتى «أكبر أمر»).'],['أكثر من الهدف','بيع الزائد — وكل بيعة بربحها المحقق.'],['الهامش','فرق صغير لا يتحرك البوت داخله.'],
           ['الحدود','الميزانية · مكابح الانهيار (لا شراء بعد نزول كبير خلال 24 ساعة) · الحماية (لا شراء فوق سعر البداية).']],
    btns:['va_now','pause_rec','va_set','va_exit','table','hist','chart','pw','cset','del'],
    faq:[['ما الفرق بينه وبين الشراء الدوري؟','الدوري يشتري المبلغ نفسه دائماً؛ مسار القيمة يشتري أكثر حين ينزل السعر وأقل — أو يبيع — حين يصعد.'],
         ['لماذا يبيع أحياناً؟','لأن صعود السعر جعل القيمة أكبر من الهدف؛ يبيع الزائد ويحقق ربحه.']]}
};
TUT.grid_plus.nums=TUT.grid_range.nums=TUT.grid_step.nums=TUT.grid.nums=1;
const TUT_FAQ=[
  ['هل يجب أن يبقى الجهاز يعمل؟','نعم. البوتات تعمل على الجهاز الذي تعمل عليه اللوحة. إن انطفأ تتوقف، وتبقى أوامرها على المنصة؛ وعند التشغيل يطابق كل بوت ما حدث ويكمل.'],
  ['ماذا لو انقطع الإنترنت؟','لا يرسل البوت أوامر جديدة، وعند عودة الاتصال يسأل المنصة عن كل أمر ويعالج ما تنفّذ.'],
  ['من أين يأتي الربح؟','من الفرق بين سعر البيع وسعر الشراء لكل صفقة، ناقص العمولة. البطاقة تعرض الربح المحقق فقط — صفقات أُغلقت.'],
  ['ما الفرق بين الربح المحقق وقيمة المحفظة؟','المحقق لا ينقص. قيمة المحفظة تتغير مع السعر لأنها تشمل العملات التي لم تُبع بعد.'],
  ['نفد الدولار — ماذا يحدث؟','رسالة واحدة للمحفظة · البطاقة تقول «🟠 ينتظر دولار» · ويُوقف الشراء تلقائياً فوق السعر بقليل ويُستأنف حين يعود الدولار (من 🛡️ الرقابة).'],
  ['ما الديمو؟','بوت بالمحرك الحقيقي نفسه على منصة وهمية بسعر OKX الحي ومحفظة وهمية — للتجربة بلا مال حقيقي، ولا يدخل في أي مجموع.'],
  ['ما الاختبار التجريبي؟','تشغيل البوت على أسعار ماضية (حقيقية أو مولّدة) خلال دقائق لترى نتيجته قبل النشر.'],
  ['كم العمولة؟','OKX تأخذ نحو 0.08% للأمر المنتظر و0.1% للفوري — لذلك يجب أن تكون مسافة الربح أكبر من ضعفها.'],
  ['هل الربح مضمون؟','لا. البوتات تربح من التذبذب، لكن إن هبط السعر كثيراً وطويلاً تبقى عملات بسعر أقل من كلفتها حتى يعود.'],
  ['هل يعمل بوتان على عملة واحدة؟','نعم وبالمحفظة نفسها، والرقابة 🛡️ تتأكد أن لكل بوت عملاته ودولاره (المتدرج: بوت واحد لكل عملة).']
];
function tutMark(el,b){if(el._tut)return;const s=el.querySelector('.cset');if(!s)return;
  const t=document.createElement('button');t.className='ctut';t.textContent='📖';t.title='📖 كيف يعمل هذا البوت — شرح ومثال متحرك وأسئلة';
  t.onclick=e=>{e.stopPropagation();openTut(b.dir)};s.parentNode.insertBefore(t,s);el._tut=1}
function openTut(dir){
  const b=(typeof botOf==='function'&&botOf(dir))||{};const k=TUT[b.bot_type]?b.bot_type:'grid',T=TUT[k];
  const ico=(b.ico)||({grid:'♾️',grid_plus:'➕',grid_range:'🎚️',grid_step:'🪜',dca_buy:'📈',dca:'📉',rec_buy:'🔁',rec_sell:'🔂',rec_va:'💹'}[k]||'🤖');
  const sec=(i,h)=>`<div class="tutsec"><h3>${i}</h3>${h}</div>`;
  let h=`<h2>📖 كيف يعمل بوت ${ico} ${T.t}${b.symbol?` — <span class="num">${b.symbol}</span>`:''}</h2>`;
  h+=sec('💡 الفكرة',T.idea.map(p=>`<p>${p}</p>`).join(''));
  h+=sec('🧩 خطوة بخطوة',`<ol class="tutsteps">${T.steps.map(s=>`<li><b>${s[0]}</b> — ${s[1]}</li>`).join('')}</ol>`);
  h+=sec('🎬 مثال متحرك',`<div class="tutanim"><svg id="tutSvg" viewBox="0 0 600 260" preserveAspectRatio="none"></svg>
    <div class="tutcap"><span id="tutEv">…</span><b id="tutPl" class="num"></b></div>
    <div class="tutctl"><button id="tutPp" onclick="tutPause()">⏸ إيقاف المثال</button><button onclick="tutRestart()">↺ من البداية</button>
    <small>مثال توضيحي بأرقام بسيطة — ليس سعراً حقيقياً</small></div></div>`);
  h+=sec('🔘 أزرار البطاقة',`<div class="tutbtns">${T.btns.map(x=>TUT_BTN[x]).filter(Boolean).map(x=>`<div><b>${x[0]}</b><span>${x[1]}</span></div>`).join('')}</div>`);
  if(T.nums)h+=sec('🧾 أرقام البطاقة',`<div class="tutbtns">${TUT_NUM.map(x=>`<div><b>${x[0]}</b><span>${x[1]}</span></div>`).join('')}</div>`);
  const qa=l=>l.map(x=>`<details class="tutqa"><summary>${x[0]}</summary><p>${x[1]}</p></details>`).join('');
  h+=sec('❓ أسئلة وأجوبة',`<div class="tutsub">عن هذا البوت</div>${qa(T.faq)}<div class="tutsub">عن البوتات كلها</div>${qa(TUT_FAQ)}`);
  showModal(h);
  if(!window._tutHM&&typeof hideModal==='function'){window._tutHM=hideModal;hideModal=function(){TUT_RUN=null;return window._tutHM.apply(this,arguments)}}   // يتوقف المثال مع إغلاق النافذة
  TUT_RUN={k:T.a,on:true,t0:0};tutRestart()}
let TUT_RUN=null;
function tutPause(){if(!TUT_RUN)return;TUT_RUN.on=!TUT_RUN.on;const b=document.getElementById('tutPp');if(b)b.textContent=TUT_RUN.on?'⏸ إيقاف المثال':'▶️ تشغيل المثال';if(TUT_RUN.on)tutLoop()}
function tutRestart(){if(!TUT_RUN)return;TUT_RUN.S=tutInit(TUT_RUN.k);TUT_RUN.last=0;if(TUT_RUN.on&&!TUT_RUN.raf)tutLoop();else tutDraw(TUT_RUN.S)}
function tutLoop(){const R=TUT_RUN;if(!R)return;R.raf=requestAnimationFrame(ts=>{R.raf=0;const svg=document.getElementById('tutSvg');
  if(!svg||!svg.isConnected||svg.offsetParent===null){TUT_RUN=null;return}
  if(!R.on)return;if(ts-R.last>=70){R.last=ts;tutStep(R.S);tutDraw(R.S)}tutLoop()})}
function tutPx(S,t){const f=S.f,sg=f.s||1;return S.P0*(1+sg*f.a*Math.sin(t/f.w1)+f.b*Math.sin(t/f.w2+1.3)+f.d*Math.sin(t/f.w3))}
function tutInit(k){
  const S={k,t:0,P0:100,pts:[],mk:[],pl:0,ev:'يبدأ البوت…',unit:'$',lv:[],hold:{},lots:[],c:null,tgt:0,q:0,cost:0,nper:0};
  const F={grid:{a:.035,b:.012,d:.008,w1:30,w2:9,w3:61,s:-1},plus:{a:.04,b:.014,d:.01,w1:30,w2:10,w3:57,s:-1},range:{a:.055,b:.01,d:.006,w1:32,w2:11,w3:70,s:-1},
    step:{a:.04,b:.012,d:.012,w1:30,w2:9,w3:66,s:-1},dcab:{a:.05,b:.01,d:.01,w1:55,w2:12,w3:80},dcas:{a:.05,b:.01,d:.01,w1:55,w2:12,w3:80},
    recb:{a:.04,b:.015,d:.01,w1:60,w2:13,w3:37},recs:{a:.04,b:.015,d:.01,w1:60,w2:13,w3:37},va:{a:.06,b:.012,d:.008,w1:70,w2:14,w3:41}};
  S.f=F[k]||F.grid;
  if(['grid','plus','range','step'].includes(k)){const g=0.012;S.g=g;S.n=k==='plus'?2:1;
    for(let i=-6;i<=6;i++)S.lv.push(+(100*Math.pow(1+g,i)).toFixed(2));
    if(k==='range'){S.lo=S.lv[2];S.hi=S.lv[9]}}
  if(k==='step')S.parts=3;
  if(k==='dcab'||k==='dcas')S.c=null;
  if(k==='va'){S.tgt=100;S.q=1;S.cost=100;S.unit='$'}
  if(k==='dcas'||k==='recs')S.unit=' عملة';
  return S}
function tutMark2(S,buy,p,txt){S.mk.push({t:S.t,p,buy});S.ev=txt}
function tutStep(S){
  const k=S.k,pPrev=S.t?tutPx(S,S.t-1):100;S.t++;const p=tutPx(S,S.t);S.pts.push(p);if(S.pts.length>140){S.pts.shift()}
  const f2=v=>v.toFixed(2);
  if(['grid','plus','range','step'].includes(k)){
    S.lv.forEach((L,i)=>{
      if(k==='range'&&(L<S.lo-1e-9||L>S.hi+1e-9))return;
      if(pPrev>L&&p<=L&&!S.hold[i]){
        if(k==='range'&&p<S.lo){S.ev='السعر تحت الحد الأدنى — لا شراء حتى يعود داخل المدى';return}
        if(k==='step'){S.hold[i]=[1,1,1];tutMark2(S,true,L,`🟢 شراء ${S.parts} أجزاء عند ${f2(L)} · بيعاتها: ${f2(L*1.006)} · ${f2(L*1.012)} · ${f2(L*1.018)}`)}
        else{const sp=S.lv[i+S.n]||L*Math.pow(1+S.g,S.n);S.hold[i]=sp;tutMark2(S,true,L,`🟢 شراء عند ${f2(L)} ⇐ بيعه يُنشر عند ${f2(sp)}${k==='plus'?' (بعد فجوة درجتين)':''}`)}}});
    Object.keys(S.hold).forEach(i=>{const L=S.lv[i],h=S.hold[i];
      if(k==='step'){h.forEach((on,j)=>{const sp=L*(1+0.006*(j+1));if(on&&pPrev<sp&&p>=sp){h[j]=0;S.pl+=(sp-L)/3;tutMark2(S,false,sp,`🔴 بيع الجزء ${j+1} عند ${f2(sp)} · ربحه ${f2((sp-L)/3)}$`)}});
        if(!h.some(Boolean))delete S.hold[i]}
      else if(pPrev<h&&p>=h){if(k==='range'&&h>S.hi+1e-9)return;S.pl+=h-L;delete S.hold[i];tutMark2(S,false,h,`🔴 بيع عند ${f2(h)} · ربح الدورة ${f2(h-L)}$ ⇐ يعود الشراء إلى ${f2(L)}`)}})}
  else if(k==='dcab'||k==='dcas'){const buy=k==='dcab',dev=[0.012,0.026,0.045,0.07],sz=[1,1.4,2,2.8],tp=0.012;
    if(!S.c){if(S.t%40===1){S.c={q:1,cost:p,base:p,i:0};tutMark2(S,buy,p,`${buy?'🟢 شراء':'🔴 بيع'} الأمر الأولي عند ${f2(p)} — تبدأ دورة`)}}
    else{const c=S.c,nx=c.i<dev.length?c.base*(1+(buy?-1:1)*dev[c.i]):null;
      if(nx&&(buy?p<=nx:p>=nx)){c.cost=(c.cost*c.q+nx*sz[c.i])/(c.q+sz[c.i]);c.q+=sz[c.i];c.i++;tutMark2(S,buy,nx,`${buy?'🟢 أمر أمان':'🔴 أمر أمان'} ${c.i} عند ${f2(nx)} · المتوسط ${f2(c.cost)} · الهدف ${f2(c.cost*(1+(buy?tp:-tp)))}`)}
      const tg=c.cost*(1+(buy?tp:-tp));
      if(buy?p>=tg:p<=tg){const pr=buy?(tg-c.cost)*c.q:c.q*(c.cost/tg-1);S.pl+=pr;tutMark2(S,!buy,tg,`${buy?'🔴 بيع الكل':'🟢 إعادة شراء الكل'} عند ${f2(tg)} · ربح الدورة ${pr.toFixed(buy?2:4)}${buy?'$':' عملة'} — تُغلق الدورة`);S.c=null}}}
  else if(k==='recb'||k==='recs'){const buy=k==='recb',tp=0.015;
    if(S.t%35===1){S.lots.push({p,tg:p*(1+(buy?tp:-tp))});tutMark2(S,buy,p,`⏰ الموعد: ${buy?'🟢 شراء':'🔴 بيع'} 10$ عند ${f2(p)} · هدفه ${f2(p*(1+(buy?tp:-tp)))}`)}
    S.lots=S.lots.filter(l=>{if(buy?p>=l.tg:p<=l.tg){const pr=buy?10*(l.tg/l.p-1):(10/l.tg-10/l.p);S.pl+=pr;tutMark2(S,!buy,l.tg,`${buy?'🔴 بيع':'🟢 إعادة شراء'} أمر عند ${f2(l.tg)} · ربحه ${pr.toFixed(buy?2:4)}${buy?'$':' عملة'}`);return false}return true})}
  else if(k==='va'){if(S.t%30===1){S.nper++;S.tgt=100+10*S.nper;const val=S.q*p,d=S.tgt-val;
    if(d>2){const u=Math.min(d,25);S.q+=u/p;S.cost+=u;tutMark2(S,true,p,`🎯 الهدف ${S.tgt}$ · القيمة ${val.toFixed(1)}$ ⇐ 🟢 شراء الفرق ${u.toFixed(1)}$`)}
    else if(d<-2){const u=Math.min(-d,25),qs=u/p,avg=S.cost/S.q;S.pl+=qs*(p-avg);S.cost-=qs*avg;S.q-=qs;tutMark2(S,false,p,`🎯 الهدف ${S.tgt}$ · القيمة ${val.toFixed(1)}$ ⇐ 🔴 بيع الزائد ${u.toFixed(1)}$ · ربحه ${(qs*(p-avg)).toFixed(2)}$`)}
    else S.ev=`🎯 الهدف ${S.tgt}$ · القيمة ${val.toFixed(1)}$ — داخل الهامش، لا شيء`}}
  S.mk=S.mk.filter(m=>S.t-m.t<140);if(S.t>1400)Object.assign(S,tutInit(k))}
function tutDraw(S){const svg=document.getElementById('tutSvg');if(!svg)return;const W=600,H=260,lo=S.P0*0.9,hi=S.P0*1.1;
  const y=p=>H-8-(p-lo)/(hi-lo)*(H-16),n=S.pts.length,x=i=>W-6-(n-1-i)*(W-12)/139,xt=t=>x(n-1-(S.t-t));
  let h='';
  (S.lv||[]).forEach((L,i)=>{const out=S.k==='range'&&(L<S.lo-1e-9||L>S.hi+1e-9);if(out)return;
    h+=`<line x1="0" x2="${W}" y1="${y(L)}" y2="${y(L)}" style="stroke:rgb(var(--${L<S.P0?'green':'red'}-rgb)/.28);stroke-dasharray:4 4"/>`});
  if(S.k==='range')[S.lo,S.hi].forEach(v=>{h+=`<line x1="0" x2="${W}" y1="${y(v)}" y2="${y(v)}" style="stroke:var(--amber);stroke-width:1.5"/>`});
  if(S.c){const tg=S.c.cost*(1+(S.k==='dcab'?0.012:-0.012));h+=`<line x1="0" x2="${W}" y1="${y(S.c.cost)}" y2="${y(S.c.cost)}" style="stroke:var(--vio);stroke-dasharray:6 3"/><line x1="0" x2="${W}" y1="${y(tg)}" y2="${y(tg)}" style="stroke:var(--amber);stroke-dasharray:2 3"/>`}
  (S.lots||[]).forEach(l=>{h+=`<line x1="0" x2="${W}" y1="${y(l.tg)}" y2="${y(l.tg)}" style="stroke:rgb(var(--amber-rgb)/.35);stroke-dasharray:2 4"/>`});
  if(n>1)h+=`<polyline fill="none" style="stroke:var(--cyan);stroke-width:2" points="${S.pts.map((p,i)=>x(i).toFixed(1)+','+y(p).toFixed(1)).join(' ')}"/>`;
  S.mk.forEach(m=>{const X=xt(m.t);if(X<0)return;h+=`<circle cx="${X}" cy="${y(m.p)}" r="5" style="fill:var(--${m.buy?'green':'red'});stroke:var(--bg1);stroke-width:1.5"/>`});
  if(n)h+=`<circle cx="${x(n-1)}" cy="${y(S.pts[n-1])}" r="4" style="fill:var(--tx)"/>`;
  if(S.k==='va'){const val=S.q*(S.pts[n-1]||100),m=200;h+=`<rect x="8" y="${H-10-S.tgt/m*80}" width="14" height="${S.tgt/m*80}" style="fill:rgb(var(--vio-rgb)/.6)"/><rect x="26" y="${H-10-val/m*80}" width="14" height="${val/m*80}" style="fill:rgb(var(--cyan-rgb)/.6)"/>`}
  svg.innerHTML=h;const e=document.getElementById('tutEv'),pl=document.getElementById('tutPl');
  if(e)e.textContent=S.ev;if(pl)pl.textContent=(S.unit===' عملة'?'الربح: '+S.pl.toFixed(4)+' عملة':'الربح: '+S.pl.toFixed(2)+'$')}
'''

CSS = r'''.ctut{font-size:15px}
.tutsec{margin:14px 0 4px}.tutsec h3{margin:0 0 8px;font-size:16px;color:var(--vio)}.tutsec p{margin:0 0 8px;line-height:1.9;color:var(--tx2)}
.tutsteps{margin:0;padding-inline-start:22px;line-height:1.9}.tutsteps li{margin:0 0 6px;color:var(--tx2)}.tutsteps b{color:var(--tx)}
.tutanim{border:1px solid var(--line);border-radius:14px;padding:10px;background:var(--card2)}
.tutanim svg{width:100%;height:220px;display:block;border-radius:10px;background:var(--chart-bg)}
.tutcap{display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap;margin-top:8px;min-height:44px;font-size:13px;line-height:1.7}
.tutcap b{color:var(--green);white-space:nowrap}.tutctl{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-top:6px}
.tutctl button{font-size:12px;padding:6px 12px}.tutctl small{color:var(--mut2);font-size:11px}
.tutbtns{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:8px}
.tutbtns>div{border:1px solid var(--line);border-radius:12px;padding:9px 11px;display:flex;flex-direction:column;gap:4px;background:rgb(var(--surf-rgb)/.5)}
.tutbtns b{color:var(--tx)}.tutbtns span{color:var(--mut);font-size:12.5px;line-height:1.75}
.tutsub{margin:10px 0 6px;font-weight:800;color:var(--cyan);font-size:13px}
.tutqa{border:1px solid var(--line);border-radius:12px;padding:8px 12px;margin:0 0 6px;background:rgb(var(--surf-rgb)/.4)}
.tutqa summary{cursor:pointer;font-weight:700;color:var(--tx)}.tutqa p{margin:8px 0 2px;color:var(--tx2);line-height:1.85}
'''

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    a = "function walletKey(b){"
    b2 = "    updCard(el,b,bench);skinUpd(el,b);caNumChk(el,b);demoMark(el,b)});"
    c = ".chip.demo{color:var(--cyan);border-color:var(--line2)}"
    for x in (a, b2, c):
        if s.count(x) != 1:
            print(f"❌ anchor found {s.count(x)} times — nothing written: {x[:80]!r}"); sys.exit(1)
    s = s.replace(a, JS + a)
    s = s.replace(b2, "    updCard(el,b,bench);skinUpd(el,b);caNumChk(el,b);demoMark(el,b);tutMark(el,b)});   // 📖 v3.36.46")
    s = s.replace(c, c + "\n" + CSS.strip())
    if '"""' in JS or '"""' in CSS:
        print("❌ triple quotes inside the page text"); sys.exit(1)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ the tutorial (9 kinds · {JS.count('[') // 2} items) · compiles · {p}")
