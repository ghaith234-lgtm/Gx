# 🎯 patch 121 (dashboard v3.36.71 · the indicators in plain words · one tab · one setting). The owner (21-11): «اريد المؤشرات مفهومة
#   وسهلة وكلامها مفهوم واي مؤشرات جديدة انضيفها بالمستقبل لان حاليا صاير عشوائية كذلك تعتمد التوقعات عليها ابدي» — and before it:
#   «نعم خليه على النسبة · ما الفرق بين الصورتين لماذا عزلت كل واحدة عن الأخرى مو المفروض كلها مؤشرات؟ · ادمجهم».
#   · EVERY indicator (the 36 systems · the ten · 🔮 · 🧲 · 💪 · 🌊 · 😨 · 🗞️ · 🏦 — 67 codes) has ONE plain entry: its name for a rise and
#     for a fall in plain Arabic · what it means in one sentence each · its technical name (small, for those who know it) · its family
#     (📈 الاتجاه · ⚡ قوة الحركة · 🎢 الابتعاد عن المعتاد · 🕯️ شكل الشموع والمستويات · 💧 السيولة والحجم · 🏦 المحترفون والعقود ·
#     🌐 السوق كله والاقتصاد) — the same names everywhere (the window · the notifications · the record · the CSV)
#     · a future indicator without its entry fails devtests/t_plain.py (the rule is in HANDOFF)
#   · ONE tab «🎯 المؤشرات» instead of «📈 المؤشرات العشرة» + «🎯 الإشارات الشغّالة»: per coin «📊 اتجاه المؤشرات الآن» (the ten's
#     average — a description of now, not a forecast) and then every indicator ON NOW grouped by family: the ten's state + every signal
#     active on the daily or the 4-hour candles, each with its plain name, its meaning and its record (right X of Y times · random)
#   · ⚙️ الإشعارات keeps ONE setting: «🎯 لا يصلك إلا ما صدق في X% من المرات أو أكثر» (+ the weekly estimate) — «أقل عدد مرات» (15) and
#     «أفضل من العشوائي» (always on) are fixed inside (SG_MINC · SG_RNDC)
#   python3 devtests/step/patches/p121_plain_indicators.py Holy_Dashboard.pyw
import sys

NM = r'''_SG_NM = {   # 🎯 v3.36.71: الأنظمة الـ36 بكلام واضح — (اسم الصعود · اسم الهبوط · معناه للصعود · معناه للهبوط) · الاسم الفني من SYS
    "08": ("قوة الحركة أصبحت صاعدة", "قوة الحركة أصبحت هابطة",
           "مقياسان لسرعة الحركة أصبحا فوق الصفر معاً — المشترون يتقدمون", "مقياسان لسرعة الحركة أصبحا تحت الصفر معاً — البائعون يتقدمون"),
    "09": ("المتوسط السريع عبر فوق الأبطأ", "المتوسط السريع عبر تحت الأبطأ",
           "متوسط آخر 5 شموع أصبح فوق متوسط آخر 13 — بداية صعود قصير", "متوسط آخر 5 شموع أصبح تحت متوسط آخر 13 — بداية هبوط قصير"),
    "10": ("عبور منتصف النطاق صعوداً بقوة", "عبور منتصف النطاق هبوطاً بقوة",
           "تجاوز السعر منتصف نطاق حركته المعتاد مع دفع صاعد", "نزل السعر تحت منتصف نطاق حركته المعتاد مع دفع هابط"),
    "11": ("قوة الشراء تجاوزت المنتصف مع الاتجاه", "قوة البيع تجاوزت المنتصف مع الاتجاه",
           "مقياس قوة الشراء صعد فوق 50 والاتجاه صاعد", "مقياس قوة الشراء نزل تحت 50 والاتجاه هابط"),
    "12": ("خط الاتجاه انقلب إلى الصعود", "خط الاتجاه انقلب إلى الهبوط",
           "خط الوقف المتحرك أصبح تحت السعر والسعر فوق متوسط 150 شمعة", "خط الوقف المتحرك أصبح فوق السعر والسعر تحت متوسط 150 شمعة"),
    "13": ("المتوسطات القصيرة والطويلة كلها صاعدة", "المتوسطات القصيرة والطويلة كلها هابطة",
           "مجموعتا المتوسطات مرتبتان للصعود — اتجاه صاعد منظم", "مجموعتا المتوسطات مرتبتان للهبوط — اتجاه هابط منظم"),
    "14": ("ارتداد من أسفل النطاق بعد بيع مبالغ فيه", "تراجع من أعلى النطاق بعد شراء مبالغ فيه",
           "لمس السعر الحد الأدنى لنطاقه المعتاد والبيع مفرط ثم ارتد", "لمس السعر الحد الأعلى لنطاقه المعتاد والشراء مفرط ثم تراجع"),
    "15": ("اختراق أعلى نطاق الحركة", "كسر أسفل نطاق الحركة",
           "أغلق السعر فوق الحد الأعلى لنطاق حركته المعتاد — انطلاق صاعد", "أغلق السعر تحت الحد الأدنى لنطاق حركته المعتاد — انطلاق هابط"),
    "16": ("انتهاء تصحيح داخل اتجاه صاعد", "انتهاء ارتداد داخل اتجاه هابط",
           "نزل السعر إلى مستوى تصحيح معتاد والوقف المتحرك ما زال صاعداً", "صعد السعر إلى مستوى ارتداد معتاد والوقف المتحرك ما زال هابطاً"),
    "17": ("اختراق أول مقاومة مع اتجاه صاعد", "كسر أول دعم مع اتجاه هابط",
           "تجاوز السعر أول مستوى مقاومة والمتوسطات الطويلة صاعدة", "نزل السعر تحت أول مستوى دعم والمتوسطات الطويلة هابطة"),
    "18": ("عودة قوية من تحت النطاق", "عودة قوية من فوق النطاق",
           "خرج السعر تحت نطاقه المعتاد ثم عاد إليه بشمعة قوية", "خرج السعر فوق نطاقه المعتاد ثم عاد إليه بشمعة قوية"),
    "19": ("عبور منتصف النطاق صعوداً بتأكيد الدفع", "عبور منتصف النطاق هبوطاً بتأكيد الدفع",
           "عبر السعر منتصف نطاق حركته ومقياسا الدفع يؤكدان الصعود", "عبر السعر منتصف نطاق حركته ومقياسا الدفع يؤكدان الهبوط"),
    "20": ("شمعة صاعدة ابتلعت الهابطة قبلها", "شمعة هابطة ابتلعت الصاعدة قبلها",
           "شمعة خضراء أكبر من الحمراء التي قبلها بالكامل — المشترون استعادوا السيطرة", "شمعة حمراء أكبر من الخضراء التي قبلها بالكامل — البائعون استعادوا السيطرة"),
    "21": ("مقياس التشبع يرتد من القاع", "مقياس التشبع ينقلب من القمة",
           "موقع السعر داخل مداه الأخير ارتد صعوداً من منطقة البيع المفرط", "موقع السعر داخل مداه الأخير انقلب هبوطاً من منطقة الشراء المفرط"),
    "22": ("اندفاع سريع للأعلى", "اندفاع سريع للأسفل",
           "حركة صاعدة سريعة وقوية في شموع قليلة", "حركة هابطة سريعة وقوية في شموع قليلة"),
    "23": ("الدفع والمتوسطات تتفق على الصعود", "الدفع والمتوسطات تتفق على الهبوط",
           "مقياسا الدفع موجبان وشريط المتوسطات صاعد", "مقياسا الدفع سالبان وشريط المتوسطات هابط"),
    "24": ("ارتداد من البيع المفرط فوق متوسط 50", "انقلاب من الشراء المفرط تحت متوسط 50",
           "مقياس التشبع ارتد من القاع والسعر فوق متوسط آخر 50 شمعة", "مقياس التشبع انقلب من القمة والسعر تحت متوسط آخر 50 شمعة"),
    "25": ("اتجاه صاعد تؤكده ثلاثة مقاييس", "اتجاه هابط تؤكده ثلاثة مقاييس",
           "الوقف المتحرك صاعد والسعر فوق متوسط 100 شمعة والدفع موجب", "الوقف المتحرك هابط والسعر تحت متوسط 100 شمعة والدفع سالب"),
    "26": ("ارتداد من المتوسط في اتجاه صاعد", "رفض عند المتوسط في اتجاه هابط",
           "نزل السعر إلى متوسط 50 شمعة وارتد منه والاتجاه صاعد", "صعد السعر إلى متوسط 50 شمعة ورُفض عنده والاتجاه هابط"),
    "27": ("الوقف المتحرك انقلب إلى الصعود", "الوقف المتحرك انقلب إلى الهبوط",
           "أصبح الوقف المتحرك تحت السعر ومقياس الدفع يؤكد", "أصبح الوقف المتحرك فوق السعر ومقياس الدفع يؤكد"),
    "28": ("تصحيح قصير داخل صعود", "ارتداد قصير داخل هبوط",
           "نزل السعر إلى متوسط 21 شمعة في اتجاه صاعد واضح", "صعد السعر إلى متوسط 21 شمعة في اتجاه هابط واضح"),
    "29": ("تقاطع صاعد فوق المستوى المحوري", "تقاطع هابط تحت المستوى المحوري",
           "المتوسط السريع عبر فوق الأبطأ والسعر فوق مستوى المحور اليومي", "المتوسط السريع عبر تحت الأبطأ والسعر تحت مستوى المحور اليومي"),
    "30": ("السعر أصبح في النصف الأعلى من مداه", "السعر أصبح في النصف الأدنى من مداه",
           "الإغلاقات تقترب من أعلى المدى الأخير", "الإغلاقات تقترب من أدنى المدى الأخير"),
    "31": ("قاع جديد واضح فوق المستوى المحوري", "قمة جديدة واضحة تحت المستوى المحوري",
           "تكوّن قاع (شمعة أدنى من جاراتها) والسعر فوق مستوى المحور", "تكوّنت قمة (شمعة أعلى من جاراتها) والسعر تحت مستوى المحور"),
    "32": ("صعود قوي بحجم تداول كبير", "هبوط حاد بحجم تداول كبير",
           "شمعة صاعدة كبيرة وحجم التداول أعلى من المعتاد بكثير", "شمعة هابطة كبيرة وحجم التداول أعلى من المعتاد بكثير"),
    "33": ("تقاطع صاعد فوق المتوسط الأطول", "تقاطع هابط تحت المتوسط الأطول",
           "متوسط 10 عبر فوق متوسط 25 والسعر فوق متوسط 50 والوقف المتحرك صاعد", "متوسط 10 عبر تحت متوسط 25 والسعر تحت متوسط 50 والوقف المتحرك هابط"),
    "34": ("تقاطع صاعد مؤكد بشمعة كاملة", "تقاطع هابط مؤكد بشمعة كاملة",
           "متوسط 9 عبر فوق متوسط 21 وأغلقت شمعة كاملة فوقهما", "متوسط 9 عبر تحت متوسط 21 وأغلقت شمعة كاملة تحتهما"),
    "35": ("الدفع انقلب صاعداً فوق متوسط 20", "الدفع انقلب هابطاً تحت متوسط 20",
           "خطا الدفع تقاطعا صعوداً والسعر فوق متوسط 20 شمعة", "خطا الدفع تقاطعا هبوطاً والسعر تحت متوسط 20 شمعة"),
    "36": ("الدفع انقلب صاعداً قرب المتوسط الطويل", "الدفع انقلب هابطاً قرب المتوسط الطويل",
           "خطا الدفع تقاطعا صعوداً والسعر قرب متوسط 100 شمعة", "خطا الدفع تقاطعا هبوطاً والسعر قرب متوسط 100 شمعة"),
    "37": ("عودة إلى منطقة المتوسطات في صعود قوي", "عودة إلى منطقة المتوسطات في هبوط قوي",
           "السعر داخل منطقة متوسطي 10 و21 والاتجاه الصاعد قوي", "السعر داخل منطقة متوسطي 10 و21 والاتجاه الهابط قوي"),
    "38": ("كسر خط الهبوط", "كسر خط الصعود",
           "تجاوز السعر الخط الذي يصل القمم الهابطة — قد ينتهي الهبوط", "نزل السعر تحت الخط الذي يصل القيعان الصاعدة — قد ينتهي الصعود"),
    "39": ("شمعة انعكاس صاعدة عند البيع المفرط", "شمعة انعكاس هابطة عند الشراء المفرط",
           "شكل شمعة يدل على رفض الهبوط ومقياس التشبع منخفض", "شكل شمعة يدل على رفض الصعود ومقياس التشبع مرتفع"),
    "40": ("المتوسطات والقوة والدفع تتفق على الصعود", "المتوسطات والقوة والدفع تتفق على الهبوط",
           "ثلاثة مقاييس مختلفة صاعدة معاً: المتوسطات وقوة الشراء والدفع", "ثلاثة مقاييس مختلفة هابطة معاً: المتوسطات وقوة الشراء والدفع"),
    "41": ("ارتداد من التشبع مع اتجاه طويل صاعد", "انقلاب من التشبع مع اتجاه طويل هابط",
           "مقياس التشبع ارتد من القاع والمتوسطات الطويلة صاعدة", "مقياس التشبع انقلب من القمة والمتوسطات الطويلة هابطة"),
    "42": ("اختراق منطقة خط الاتجاه", "كسر منطقة خط الاتجاه",
           "تجاوز السعر منطقة الوقف المتحرك صعوداً", "نزل السعر تحت منطقة الوقف المتحرك"),
    "43": ("نزول حاد تحت قاعدة سعرية (فرصة ارتداد)", "صعود حاد فوق قمة سعرية (فرصة تراجع)",
           "كسر السعر قاعاً سابقاً ثابتاً بنسبة كبيرة — يُشترى عادة على أمل الارتداد", "تجاوز السعر قمة سابقة ثابتة بنسبة كبيرة — يُتوقع عادة تراجعه"),
}
_SG_XNM = {   # 🎯 v3.36.71: (الأسرة · اسم الصعود · اسم الهبوط · معناه للصعود · معناه للهبوط · الاسم الفني) — المؤشرات العشرة وكل ما ليس من الـ36
    "O-vp": ("pattern", "📊 السعر فوق منطقة أكثر التداول", "📊 السعر تحت منطقة أكثر التداول",
             "أغلب التداول الأخير جرى تحت السعر الحالي فأصبحت تلك المنطقة دعماً", "أغلب التداول الأخير جرى فوق السعر الحالي فأصبحت تلك المنطقة مقاومة", "Volume Profile"),
    "O-avwap": ("pattern", "⚓ المشترون منذ آخر قاع وقمة رابحون", "⚓ المشترون منذ آخر قاع وقمة خاسرون",
                "السعر فوق متوسط سعر التداول منذ آخر قاع ومنذ آخر قمة — المشترون مسيطرون", "السعر تحت متوسط سعر التداول منذ آخر قاع ومنذ آخر قمة — البائعون مسيطرون", "Anchored VWAP"),
    "O-of": ("volume", "🌊 صفقات الشراء أقوى من البيع", "🌊 صفقات البيع أقوى من الشراء",
             "في آخر 24 ساعة غلبت صفقات الشراء ودفتر الأوامر يدعمها", "في آخر 24 ساعة غلبت صفقات البيع ودفتر الأوامر يدعمها", "Order Flow"),
    "O-pa": ("pattern", "🕯️ قمم وقيعان أعلى", "🕯️ قمم وقيعان أدنى",
             "كل قمة وكل قاع أعلى من السابق — هذا شكل الصعود", "كل قمة وكل قاع أدنى من السابق — هذا شكل الهبوط", "Price Action"),
    "O-trend": ("trend", "📈 الاتجاه العام صاعد", "📈 الاتجاه العام هابط",
                "السعر فوق متوسط آخر 200 شمعة — الصورة الكبيرة صاعدة", "السعر تحت متوسط آخر 200 شمعة — الصورة الكبيرة هابطة", "EMA 50/200"),
    "O-st": ("trend", "🟩 خط الاتجاه أخضر", "🟩 خط الاتجاه أحمر",
             "خط وقف متحرك تحت السعر يتبعه صعوداً — الاتجاه صاعد ما لم يُكسر", "خط وقف متحرك فوق السعر يتبعه هبوطاً — الاتجاه هابط ما لم يُخترق", "Supertrend"),
    "O-macd": ("momentum", "⚡ قوة الدفع تزداد صعوداً", "⚡ قوة الدفع تزداد هبوطاً",
               "الفرق بين متوسط سريع وآخر بطيء يتسع للأعلى — الصعود يتسارع", "الفرق بين متوسط سريع وآخر بطيء يتسع للأسفل — الهبوط يتسارع", "MACD"),
    "O-rsi": ("momentum", "💪 قوة الشراء هي الغالبة", "💪 قوة البيع هي الغالبة",
              "مقياس قوة الشراء (من 0 إلى 100) يميل إلى الشراء", "مقياس قوة الشراء (من 0 إلى 100) يميل إلى البيع", "RSI"),
    "O-adx": ("trend", "🧭 يوجد اتجاه صاعد حقيقي", "🧭 يوجد اتجاه هابط حقيقي",
              "قوة الاتجاه فوق 25 والاتجاه صاعد — ليس تذبذباً عشوائياً", "قوة الاتجاه فوق 25 والاتجاه هابط — ليس تذبذباً عشوائياً", "ADX"),
    "O-cmf": ("volume", "💧 الأموال تدخل العملة", "💧 الأموال تخرج من العملة",
              "الإغلاقات قريبة من أعلى الشموع مع حجم جيد — مال يدخل", "الإغلاقات قريبة من أدنى الشموع مع حجم جيد — مال يخرج", "CMF"),
    "O-verdict": ("trend", "📊 معدل المؤشرات العشرة: صعود", "📊 معدل المؤشرات العشرة: هبوط",
                  "متوسط المؤشرات العشرة الموزون تجاوز +15 من 100", "متوسط المؤشرات العشرة الموزون نزل تحت −15 من 100", ""),
    "O-bottom": ("volatility", "🟢 مؤشر القاع", "🟢 مؤشر القاع",
                 "هبوط كبير وبيع مفرط ثم بداية ارتداد — مؤشر القاع تجاوز 50 من 100", "هبوط كبير وبيع مفرط ثم بداية ارتداد — مؤشر القاع تجاوز 50 من 100", ""),
    "O-botv": ("volume", "🟢 القاع المؤكد بالحجم", "🟢 القاع المؤكد بالحجم",
               "مؤشر القاع مع حجم تداول أعلى من المعتاد — المشترون دخلوا بقوة", "مؤشر القاع مع حجم تداول أعلى من المعتاد — المشترون دخلوا بقوة", ""),
    "F-lc": ("pattern", "🧠 حالات الماضي المشابهة صعدت", "🧠 حالات الماضي المشابهة هبطت",
             "أقرب الحالات شبهاً بالوضع الحالي في تاريخ العملة انتهت أغلبها بصعود", "أقرب الحالات شبهاً بالوضع الحالي في تاريخ العملة انتهت أغلبها بهبوط", "Lorentzian"),
    "F-nw": ("trend", "〰️ خط السعر الناعم يتجه للأعلى", "〰️ خط السعر الناعم يتجه للأسفل",
             "خط يرسم حركة السعر بلا ضجيج انقلب صاعداً", "خط يرسم حركة السعر بلا ضجيج انقلب هابطاً", "Nadaraya–Watson"),
    "F-vote": ("trend", "🔮 أغلب قراءات التوقعات: صعود", "🔮 أغلب قراءات التوقعات: هبوط",
               "أغلب قراءات نافذة التوقعات تميل إلى الصعود", "أغلب قراءات نافذة التوقعات تميل إلى الهبوط", ""),
    "X-ad": ("volume", "🧲 السيولة تدخل والسعر لم يتحرك بعد (تجميع)", "🔻 السيولة تخرج والسعر لم ينزل بعد (تصريف)",
             "حجم الشراء يتراكم أياماً والسعر شبه ثابت — كأن أحداً يجمع بهدوء", "حجم البيع يتراكم أياماً والسعر شبه ثابت — كأن أحداً يبيع بهدوء", "A/D"),
    "X-adt": ("volume", "🧲 صعود مدعوم بدخول السيولة", "🧲 نزول مدعوم بخروج السيولة",
              "السعر يصعد والسيولة الداخلة تؤكد الصعود", "السعر ينزل والسيولة الخارجة تؤكد النزول", "A/D"),
    "X-rs": ("momentum", "💪 أقوى من البيتكوين", "💪 أضعف من البيتكوين",
             "العملة تصعد أكثر من البيتكوين أو تنزل أقل منه منذ مدة", "العملة تصعد أقل من البيتكوين أو تنزل أكثر منه منذ مدة", ""),
    "W-crash": ("market", "🌊 انهيار السوق كله", "🌊 انهيار السوق كله",
                "ثلث العملات أو أكثر هبطت بقوة غير معتادة في الشمعة نفسها", "ثلث العملات أو أكثر هبطت بقوة غير معتادة في الشمعة نفسها", ""),
    "M-fng": ("market", "😨 خوف في السوق", "🤑 طمع في السوق",
              "مؤشر الخوف والطمع منخفض — الناس خائفون، وقد يسبق ذلك ارتداداً", "مؤشر الخوف والطمع مرتفع — الناس متحمسون، وقد يسبق ذلك تراجعاً", "Fear & Greed"),
    "M-vix": ("market", "😱 أسواق الأسهم هادئة", "😱 أسواق الأسهم قلقة",
              "مقياس الخوف في الأسهم الأمريكية منخفض — المال يميل إلى المخاطرة", "مقياس الخوف في الأسهم الأمريكية مرتفع — المال يبتعد عن المخاطرة", "VIX"),
    "M-dxy": ("market", "💱 الدولار يضعف", "💱 الدولار يقوى",
              "مؤشر الدولار ينزل — يساعد العملات الرقمية عادة", "مؤشر الدولار يصعد — يضغط على العملات الرقمية عادة", "DXY"),
    "M-us10": ("market", "📜 فائدة السندات الأمريكية تنزل", "📜 فائدة السندات الأمريكية تصعد",
               "عائد سندات العشر سنوات ينزل — المال يميل إلى الأصول الخطرة", "عائد سندات العشر سنوات يصعد — المال يميل إلى الأمان", "US10Y"),
    "M-epu": ("market", "🏛️ عدم اليقين الاقتصادي منخفض", "🏛️ عدم اليقين الاقتصادي مرتفع",
              "أخبار السياسات الاقتصادية هادئة", "أخبار السياسات الاقتصادية مضطربة", "EPU"),
    "M-gpr": ("market", "🌍 التوترات العالمية منخفضة", "🌍 التوترات العالمية مرتفعة",
              "مقياس الحروب والتوترات بين الدول منخفض", "مقياس الحروب والتوترات بين الدول مرتفع", "GPR"),
    "M-tone": ("market", "📰 نبرة الأخبار إيجابية", "📰 نبرة الأخبار سلبية",
               "الأخبار العالمية تميل إلى التفاؤل", "الأخبار العالمية تميل إلى التشاؤم", "GDELT"),
    "P-ls": ("market", "⚖️ ازدحام البيع في العقود (قراءة عكسية)", "⚖️ ازدحام الشراء في العقود (قراءة عكسية)",
             "أغلب حسابات العقود تبيع — وحين يزدحم الناس على جهة يتحرك السعر غالباً عكسها", "أغلب حسابات العقود تشتري — وحين يزدحم الناس على جهة يتحرك السعر غالباً عكسها", "Long/Short"),
    "P-tk": ("market", "🐂 الشراء العدواني في العقود", "🐻 البيع العدواني في العقود",
             "صفقات الشراء الفورية بسعر السوق تغلب البيع في العقود", "صفقات البيع الفورية بسعر السوق تغلب الشراء في العقود", "Taker volume"),
    "P-pc": ("market", "🎲 الخيارات تميل للصعود", "🎲 الخيارات تميل للهبوط",
             "عقود الخيارات على الصعود أكثر من عقود الهبوط", "عقود الخيارات على الهبوط أكثر من عقود الصعود", "Put/Call"),
    "P-mv": ("market", "🔗 الحائزون قريبون من سعر شرائهم", "🔗 الحائزون في ربح كبير",
             "أغلب الحائزين قريبون من سعر شرائهم — ضغط البيع عادة أقل", "أغلب الحائزين في ربح كبير — قد يبيع بعضهم", "MVRV"),
}
SG_GRP = (   # 🎯 v3.36.71: أُسر العرض — (المفتاح · الأيقونة · الاسم · ماذا تقيس) · كل مؤشر جديد يُضاف إلى إحداها
    ("trend", "📈", "الاتجاه", "هل السعر في صعود أم هبوط على مدى أطول"),
    ("momentum", "⚡", "قوة الحركة", "هل الحركة تتسارع أم تضعف"),
    ("volatility", "🎢", "الابتعاد عن المعتاد", "هل ابتعد السعر كثيراً عن نطاقه المعتاد فيرتد أو ينطلق"),
    ("pattern", "🕯️", "شكل الشموع والمستويات", "القمم والقيعان وأشكال الشموع والدعوم والمقاومات"),
    ("volume", "💧", "السيولة والحجم", "هل الأموال تدخل العملة أم تخرج منها"),
    ("pro", "🏦", "المحترفون والعقود", "ماذا يفعل متداولو العقود وكبار الحائزين على هذه العملة"),
    ("market", "🌐", "السوق كله والاقتصاد", "حال السوق كله والخوف والطمع والدولار والأخبار"),
)'''

PY_PLAIN = r'''


def _sg_plain(code):
    """🎯 v3.36.71: المؤشر بكلام واضح ⇒ (أسرة العرض · اسم الصعود · اسم الهبوط · معناه للصعود · معناه للهبوط · الاسم الفني) أو None"""
    L = _sg_lib()
    if code in L.SYS:
        p = _SG_NM.get(code)
        if not p:
            return None
        return (L.SYS[code][1], p[0], p[1], p[2], p[3], L.SYS[code][0])
    x = _SG_XNM.get(code)
    if not x:
        return None
    return ("pro" if code.startswith("P-") else x[0], x[1], x[2], x[3], x[4], x[5])


def sg_plain_all():
    """كل المؤشرات بكلامها الواضح للنافذة: {الرمز: [الأسرة · الصعود · الهبوط · معنى الصعود · معنى الهبوط · الفني]}"""
    P = _SG.get("plain")
    if P is None:
        P = {}
        for c in list(_sg_lib().SYS) + list(_SG_XNM):
            p = _sg_plain(c)
            if p:
                P[c] = list(p)
        _SG["plain"] = P
    return P
'''

R = [
    # meta: the names come from the plain table (the ten too)
    ("""        M = {c: (fam, _SG_NM.get(c, (nm, nm))[0], _SG_NM.get(c, (nm, nm))[1]) for c, (nm, fam, fn) in L.SYS.items()}
        for k, nm, ic, _w, _d in _IND2_K:
            M["O-" + k] = (_SG_OLDF.get(k, "trend"), f"{ic} {nm}: صاعد", f"{ic} {nm}: هابط")
        M.update(_SG_XNM)""",
     """        M = {c: (fam, _SG_NM.get(c, (nm, nm))[0], _SG_NM.get(c, (nm, nm))[1]) for c, (nm, fam, fn) in L.SYS.items()}
        for k, nm, ic, _w, _d in _IND2_K:
            M["O-" + k] = (_SG_OLDF.get(k, "trend"), f"{ic} {nm}: صاعد", f"{ic} {nm}: هابط")
        M.update({c: x[:3] for c, x in _SG_XNM.items()})               # 🎯 v3.36.71: الأسماء الواضحة (والعشرة منها)"""),
    ("""

def _sg_name(code, side):""", PY_PLAIN + """

def _sg_name(code, side):"""),
    # one setting: the minimum count and «better than random» fixed inside
    ("""    return {"on": bool(c.get("sg_on", True)), "thr": iv("sg_thr", 65, 50, 95), "min": iv("sg_min", 15, 3, 200),
            "rnd": bool(c.get("sg_rnd", True)), "rare": bool(c.get("sg_rare", True)), "rmin": iv("sg_rmin", 6, 3, 50),""",
     """    return {"on": bool(c.get("sg_on", True)), "thr": iv("sg_thr", 65, 50, 95), "min": SG_MINC,           # 🎯 v3.36.71: إعداد واحد (النسبة)
            "rnd": SG_RNDC, "rare": bool(c.get("sg_rare", True)), "rmin": iv("sg_rmin", 6, 3, 50),"""),
    ("""def sg_cfg():
    c = _safe(app_cfg, default={}) or {}""",
     """SG_MINC = 15                                 # 🎯 v3.36.71: أقل عدد حالات (ثابت بالداخل — كان إعداداً)
SG_RNDC = True                               # 🎯 v3.36.71: أفضل من العشوائي دائماً (ثابت بالداخل — كان إعداداً)


def sg_cfg():
    c = _safe(app_cfg, default={}) or {}"""),
    ("""    msg = (("🎯 إشعارات الإشارات مفعّلة — " + f"{p['thr']}% فأكثر · {_sg_ar(p['min'], 'time')} فأكثر · " + SG_CH[p["ch"]]) if p["on"]
           else "🔕 إشعارات الإشارات متوقفة")""",
     """    msg = ((f"🎯 إشعارات المحلل مفعّلة — لا يصلك إلا ما صدق في {p['thr']}% من المرات أو أكثر · " + SG_CH[p["ch"]]) if p["on"]
           else "🔕 إشعارات المحلل متوقفة")"""),
    # the view: every single indicator on now (not cut at 80) + the plain table + the families
    ("""            rows.sort(key=lambda r: (not r["ok"], -r["lb"]))
            it["fr"][fr] = {"t": x.get("t"), "px": x.get("px"), "rows": rows[:80],""",
     """            rows.sort(key=lambda r: (not r["ok"], -r["lb"]))
            rows = [r for r in rows if len(r["k"]) == 1] + [r for r in rows if len(r["k"]) > 1][:60]      # 🎯 v3.36.71: كل مؤشر نشط
            it["fr"][fr] = {"t": x.get("t"), "px": x.get("px"), "rows": rows,"""),
    ("""    if not cat:
        v.update(cat=None, now=[], est=None)
        return v
    idx = cat["idx"]""",
     """    v["plain"], v["grp"] = sg_plain_all(), [list(g) for g in SG_GRP]                  # 🎯 v3.36.71: كل مؤشر بكلام واضح (قبل بناء السجل أيضاً)
    if not cat:
        v.update(cat=None, now=[], est=None)
        return v
    idx = cat["idx"]"""),
    # the catalog search finds the technical names and the meanings too
    ("""        if txt and txt.strip() and txt.strip().lower() not in (" ".join(r["nm"]) + " " + " ".join(e["k"])).lower():""",
     """        if txt and txt.strip() and txt.strip().lower() not in (" ".join(r["nm"]) + " " + " ".join(e["k"]) + " "
                                                                 + " ".join(" ".join(str(z) for z in (_sg_plain(k) or ())[3:]) for k in e["k"])).lower():"""),
    # ── the page ──
    ("""async function openSig(tab){return openInd(tab||'an')}                          // (الاسم القديم: الأزرار وضغط الإشعارات تفتح المحلل)""",
     """async function openSig(tab){return openInd(tab==='now'?'ind':(tab||'an'))}     // (الاسم القديم: الأزرار وضغط الإشعارات تفتح المحلل · «now» أصبح «🎯 المؤشرات»)"""),
    ("""async function openInd(tab){SGTAB=tab||'an';                                   // 🧠 v3.36.69: نافذة واحدة — المؤشرات هي المحلل (🎯 بداخلها)""",
     """async function openInd(tab){SGTAB=tab==='now'?'ind':(tab||'an');              // 🧠 v3.36.69: نافذة واحدة — المؤشرات هي المحلل · 🎯 v3.36.71: تبويب واحد للمؤشرات"""),
    ("""function sgTab(t){SGTAB=t;sgRender();if(t==='cat')sgCat()}""",
     """function sgTab(t){SGTAB=t==='now'?'ind':t;sgRender();if(SGTAB==='cat')sgCat();if(SGTAB==='ind')sgIndLoad()}
async function sgIndLoad(){clearTimeout(INDT);try{INDV=await api('/api/indicators')}catch(e){INDV=null}      // 🎯 v3.36.71: اتجاه المؤشرات العشرة لكل عملة
  if(SGTAB==='ind')sgRender();if(INDV&&INDV.busy&&!(INDV.rows||[]).length&&SGTAB==='ind'&&$('#sg_body'))INDT=setTimeout(sgIndLoad,3000)}"""),
    ("""async function sgLoad(){clearTimeout(SGT);try{SGV=await api('/api/signals')}catch(e){SGV=null}sgRender();if(SGTAB==='cat')sgCat();""",
     """async function sgLoad(){clearTimeout(SGT);try{SGV=await api('/api/signals')}catch(e){SGV=null}sgRender();if(SGTAB==='cat')sgCat();if(SGTAB==='ind'&&!INDV)sgIndLoad();"""),
    ("""  if(tb)tb.innerHTML=[['an','🧠 المحلل'],['ind','📈 المؤشرات العشرة'],['now','🎯 الإشارات الشغّالة'],['cat','📚 المجموعات'],['log','📜 السجل'],['cfg','⚙️ الإشعارات']].map(([k,t])=>`<button class="${SGTAB===k?'on':''}" onclick="sgTab('${k}')">${t}</button>`).join('');
  if(SGTAB==='ind'){el.style.cssText='text-align:right';if(!$('#ind_body')){el.innerHTML=`<div id="ind_body">${LDR('جاري الحساب…')}</div>`;indLoad()}return}
  if(!V||V.ok===false){el.innerHTML='⚠️ تعذّر تحميل المحلل';return}
  el.style.cssText='text-align:right';
  el.innerHTML=SGTAB==='an'?sgAn(V):SGTAB==='cat'?sgCatUI(V):SGTAB==='log'?sgLog(V):SGTAB==='cfg'?sgCfg(V):sgNow(V)}""",
     """  if(tb)tb.innerHTML=[['an','🧠 المحلل'],['ind','🎯 المؤشرات'],['cat','📚 المجموعات'],['log','📜 السجل'],['cfg','⚙️ الإشعارات']].map(([k,t])=>`<button class="${SGTAB===k?'on':''}" onclick="sgTab('${k}')">${t}</button>`).join('');
  if(!V||V.ok===false){el.innerHTML='⚠️ تعذّر تحميل المحلل';return}
  el.style.cssText='text-align:right';
  el.innerHTML=SGTAB==='an'?sgAn(V):SGTAB==='cat'?sgCatUI(V):SGTAB==='log'?sgLog(V):SGTAB==='cfg'?sgCfg(V):sgInd(V)}"""),
    # 🎯 the merged tab (replaces sgNow and sgCoin — «الإشارات الشغّالة» — and the old ten-indicators list inside this window)
    ("""function sgCoin(x,V){const op=!!SGO[x.sym],F=x.fr||{};""",
     """function sgPl(V,c){return ((V&&V.plain)||{})[c]||null}                     // 🎯 v3.36.71: [الأسرة · الصعود · الهبوط · معنى الصعود · معنى الهبوط · الفني]
function sgPlNm(V,c,s){const p=sgPl(V,c);return p?(s>0?p[1]:p[2]):c}
function sgIndAvg(I){if(!I)return '';const sc=Math.max(-100,Math.min(100,+I.score||0)),P=I.parts||[];      // 📊 اتجاه المؤشرات الآن (العشرة) — وصف لا توقع
  const up=P.filter(p=>+p.s>=0.15).length,dn=P.filter(p=>+p.s<=-0.15).length,acc=I.acc_bt||{};
  return `<div class="ind-avg"><div class="ind-sub">📊 <b style="color:var(--tx)">اتجاه المؤشرات الآن:</b> <span class="ind-v ${gEsc(I.verdict)}">${gEsc(I.txt)}</span> <b style="color:var(--tx)" dir="ltr">${sc>0?'+':''}${sc}</b> · ${up} صاعدة · ${dn} هابطة · ${P.length-up-dn} محايدة</div>
    <div class="ind-bar" title="معدل المؤشرات العشرة من −100 (هبوط) إلى +100 (صعود)"><i style="left:${((sc+100)/2).toFixed(1)}%"></i></div>
    <div class="ind-sub">وصف لحال المؤشرات العشرة الآن — ليس توقعاً${acc.pct!=null?` · صدقه للساعات القليلة القادمة ${acc.pct}% <small>(${acc.n})</small> وهو قريب من الصدفة`:''}</div></div>`}
function sgIndRow(V,it,hz){const p=sgPl(V,it.code)||[],r=it.r,s=it.s,mean=s>0?p[3]:p[4];
  return `<div class="sg-pl${s<0?' sell':''}"><div class="sg-plh"><span class="sg-pld">${s>0?'🟢':'🔴'}</span><b>${gEsc(sgPlNm(V,it.code,s))}</b>
      <small class="sg-fr">${gEsc(((V.fn||{})[it.f])||it.f)}</small>${r.new?'<span class="sg-b new">🆕 الآن</span>':''}${r.ok?'<span class="sg-b ok">🔔 تصلك</span>':''}</div>
    ${mean?`<div class="ind-sub">${gEsc(mean)}</div>`:''}
    <div class="sg-rec">صدق <b>${r.w}</b> من <b>${sgAr(r.n,'time')}</b> (<b>${(+r.h).toFixed(0)}%</b>) ${gEsc(hz)} · العشوائي ${(+r.rh).toFixed(0)}%${r.better?'':' · <span style="color:var(--amber)">⚠️ ليس أفضل من العشوائي</span>'}${p[5]?` <small class="sg-tech">· ${gEsc(p[5])}</small>`:''}</div></div>`}
function sgIndTen(V,p,base){const c='O-'+p.k,s=+p.s>=0.15?1:+p.s<=-0.15?-1:0,P=sgPl(V,c)||[];      // أحد المؤشرات العشرة: حاله الآن
  return `<div class="ind-row sg-pl ten${s<0?' sell':s?'':' flat'}" onclick="openGuide('${gEsc(p.k)}','ind')"><div class="sg-plh"><span class="sg-pld">${s>0?'🟢':s<0?'🔴':'⚪'}</span>
      <b>${gEsc(s?sgPlNm(V,c,s):((P[5]||p.name)+': محايد'))}</b> <small class="gd-i">ⓘ</small><small class="sg-fr">الآن</small></div>
    <div class="ind-sub">${gEsc(s>0?(P[3]||''):s<0?(P[4]||''):(p.what||''))}</div>
    <small>${gEsc(p.txt)}${p.acc!=null?` · 🎯 دقته على ${gEsc(base)}: ${p.acc}% (${p.n})`:''}${P[5]?` <span class="sg-tech">· ${gEsc(P[5])}</span>`:''}</small></div>`}
function sgIndCoin(x,V){const op=!!SGO[x.sym],F=x.fr||{},G=V.grp||[],I=((INDV&&INDV.rows)||[]).find(r=>r.sym===x.sym)||null;
  const items=[];['1D','4H'].forEach(f=>{((F[f]||{}).rows||[]).filter(r=>r.k.length===1&&sgPl(V,r.k[0])).forEach(r=>items.push({code:r.k[0],s:r.s,f,r}))});
  const nb=items.filter(i=>i.s>0).length,ns=items.filter(i=>i.s<0).length,px=(F['4H']||F['1D']||{}).px||(I&&I.px);
  let det='';
  if(op){const hz={'4H':'غداً','1D':'الشهر القادم'};
    det=`<div class="ind-det" onclick="event.stopPropagation()">${G.map(([g,ic,nm,what])=>{
        const ten=((I&&I.parts)||[]).filter(p=>(sgPl(V,'O-'+p.k)||[])[0]===g).sort((a,b)=>((b.acc??-1)-(a.acc??-1)));
        const on=items.filter(i=>(sgPl(V,i.code)||[])[0]===g).sort((a,b)=>(b.r.ok-a.r.ok)||(b.r.h-a.r.h));
        if(!ten.length&&!on.length)return '';
        return `<div class="sg-grp"><div class="sg-frh">${ic} ${gEsc(nm)} <small>— ${gEsc(what)}</small></div>${ten.map(p=>sgIndTen(V,p,x.base)).join('')}${on.map(i=>sgIndRow(V,i,hz[i.f]||'')).join('')}</div>`}).join('')
      ||'<div class="ind-sub">لا مؤشر نشط الآن على هذه العملة</div>'}
      ${I?`<div class="sg-grp"><div class="sg-frh">➕ قراءات أخرى</div>${indX(I)}${indXDet(I)}${indPDet(I)}</div>`:''}
      ${(()=>{const c=['1D','4H'].reduce((a,f)=>a+((F[f]||{}).rows||[]).filter(r=>r.k.length>1&&r.ok).length,0);return c?`<div class="an-more"><button onclick="sgTab('an')">🤝 ${c} من المجموعات المتفقة المثبتة نشطة الآن — في 🧠 المحلل ←</button></div>`:''})()}</div>`}
  return `<div class="ind-c sg-c${op?' open':''}" onclick="SGO['${gEsc(x.sym)}']=!SGO['${gEsc(x.sym)}'];sgRender()"><div class="ind-h"><span class="cn">${gEsc(x.base)}</span>${px?`<span class="px">${fmtPx(px)}</span>`:''}
    ${I?`<span class="chg ${(+I.chg24||0)>=0?'up':'dn'}">${(+I.chg24||0)>=0?'▲':'▼'}${Math.abs(+I.chg24||0).toFixed(2)}%</span>`:''}<span class="ind-sub" style="margin-inline-start:auto">${op?'':'اضغط للتفاصيل ←'}</span></div>
    ${sgIndAvg(I)}<div class="ind-dots"><span class="ind-chip">نشطة الآن: <b style="color:var(--green)">🟢 ${nb}</b> · <b style="color:var(--red)">🔴 ${ns}</b></span></div>${det}</div>`}
function sgInd(V){let h='';const B=V.busy||{};                                  // 🎯 v3.36.71: كل المؤشرات في تبويب واحد — بكلام واضح، مجمّعة بأسرها، بسجلها
  if(B.phase)h+=`<div class="sg-busy">${gEsc(B.msg||'…')}<div class="sg-pb"><i style="width:${Math.max(3,+B.pct||0)}%"></i></div></div>`;
  if(V.err)h+=`<div class="ind-sub" style="color:var(--amber)">⚠️ ${gEsc(V.err)}</div>`;
  if(INDV&&INDV.ok!==false&&INDV.on)h+=`<details class="sg-more"><summary>🌐 السوق كله الآن — الخوف والطمع · السيولة · المحترفون · الاقتصاد</summary><div style="text-align:right">${indFng(INDV.fng||{})}${indMkt(INDV.mkt)}${indPro(INDV.pro)}</div></details>`;
  const N=V.cat?(V.now||[]):[],mine=N.filter(x=>x.mine),oth=N.filter(x=>!x.mine);
  ((INDV&&INDV.rows)||[]).forEach(r=>{if(!N.some(x=>x.sym===r.sym))mine.push({sym:r.sym,base:r.base,mine:true,fr:{}})});    // المؤشرات العشرة تظهر قبل بناء السجل أيضاً
  if(!V.cat)h+=`<div class="sg-empty">🏗️ <b>أول مرة:</b> تُجلب شموع ~${(V.uni||[]).length} عملة (سنتان على 4 ساعات ونحو 7 سنوات يومية) ثم تُحسب كل المؤشرات وسجلها — بعملية منفصلة لا تُثقل اللوحة. يأخذ ذلك من ربع ساعة إلى ساعة مرة واحدة.${V.on?'':'<br>⚠️ المؤشرات وإشعارات المحلل متوقفة — شغّل أحدهما'}</div>`;
  else if(!(V.now||[]).length)h+='<div class="sg-empty">🔍 أول فحص عند إغلاق شمعة 4 ساعات القادمة (3 · 7 · 11 صباحاً ومساءً بتوقيت بغداد) أو اليومية (3 فجراً)</div>';
  if(!mine.length&&!oth.length)return h;
  if(V.cat)h+=`<div class="ind-top"><span class="ind-chip">🔄 آخر فحص ${V.scan_ts?gAgo(V.scan_ts):'—'}</span><span class="ind-chip">🎯 ${Object.keys(V.plain||{}).length} مؤشراً</span></div>`;
  h+=`<div class="ind-list">${mine.map(x=>sgIndCoin(x,V)).join('')||'<div class="ind-sub">لا توجد عملات في إشعاراتك — اخترها من ⚙️ الإشعارات</div>'}</div>`;
  if(oth.length)h+=`<details class="sg-more"><summary>عملات القياس الأخرى (${oth.length}) — تُفحص لتقوية السجل ولا تصلك إشعاراتها</summary><div class="ind-list">${oth.map(x=>sgIndCoin(x,V)).join('')}</div></details>`;
  h+=`<details class="ind-help"><summary>كيف أقرأ هذه النافذة؟</summary>
    <div>• <b>📊 اتجاه المؤشرات الآن</b>: معدل المؤشرات العشرة من −100 (هبوط) إلى +100 (صعود) — يصف الحال الآن ولا يتوقع؛ قياسه على الساعات القليلة القادمة قريب من الصدفة.</div>
    <div>• تحته <b>كل مؤشر نشط الآن</b> على العملة، مجمّعاً بأسرته (${(V.grp||[]).map(g=>g[1]+' '+gEsc(g[2])).join(' · ')}): اسمه بكلام واضح، وماذا يعني، و<b>سجله</b> — صدق كم من كم مرة على الأسعار الحقيقية (غداً على شموع 4 ساعات · الشهر القادم على اليومية) مقارنةً بالعشوائي.</div>
    <div>• 🟢 يميل إلى الصعود · 🔴 يميل إلى الهبوط · ⚪ محايد · 🔔 تصلك = يمر بنسبتك في ⚙️ الإشعارات · الاسم الفني بخط صغير لمن يعرفه.</div>
    <div>• المؤشر وحده قليل الصدق غالباً؛ <b>🧠 المحلل</b> لا يعتمد إلا على مجموعات منها تتفق وصدقت في كل فترات التاريخ.</div>
    <div style="color:var(--amber);margin-top:6px">⚠️ احتمالات لا ضمانات · اللوحة تقرأ وتنبّه فقط: لا تفتح أمراً ولا تغلقه.</div></details>`;
  return h}
function sgCoin(x,V){const op=!!SGO[x.sym],F=x.fr||{};"""),
    # ⚙️ one setting
    ("""    <div class="sg-set"><div class="sg-sh">🎚️ أقل نسبة صدق: <b id="sg_thr_v">${c.thr}%</b></div><input type="range" id="sg_thr" min="50" max="95" step="1" value="${c.thr}" oninput="sgEst({thr:+this.value})" onchange="sgSet({thr:+this.value})">
      <div class="ind-sub" id="sg_est">${sgEstTxt(V.est)}</div></div>
    <div class="sg-set"><div class="sg-sh">🔢 أقل عدد مرات حتى تُحسب نسبتها: <b id="sg_min_v">${c.min}</b></div><input type="range" id="sg_min" min="3" max="100" step="1" value="${c.min}" oninput="sgEst({min:+this.value})" onchange="sgSet({min:+this.value})">
      <div class="ind-sub">إشارة ظهرت مرتين وصدقت مرتين = 100% — صدفة. الحد يمنع ذلك.</div></div>
    <div class="sg-set">${tg(c.rnd,`sgSet({rnd:${!c.rnd}})`,'✅ أفضل من العشوائي فقط','⬜ أفضل من العشوائي فقط')}<div class="ind-sub">نسبة 55% في سوق نازل قد تكون مثل البيع العشوائي — هذا الشرط يشترط أن تكون أعلى منه بوضوح.</div></div>""",
     """    <div class="sg-set"><div class="sg-sh">🎯 لا يصلك إلا ما صدق في <b id="sg_thr_v">${c.thr}%</b> من المرات أو أكثر</div><input type="range" id="sg_thr" min="50" max="95" step="1" value="${c.thr}" oninput="sgEst({thr:+this.value})" onchange="sgSet({thr:+this.value})">
      <div class="ind-sub" id="sg_est">${sgEstTxt(V.est)}</div>
      <div class="ind-sub">النسبة الأعلى = إشعارات أقل وأصدق · 60% مناسبة لأغلب الناس · ويُشترط دائماً أن يكون قد ظهر ${sgAr(c.min,'time')} على الأقل وأن يكون أفضل من الشراء أو البيع العشوائي.</div></div>"""),
    ("""function sgEstTxt(E){if(!E)return 'التقدير يظهر بعد بناء الدليل';
  return `بهذه الإعدادات كان سيصلك أسبوعياً نحو <b>${E.cut}</b> من الإشعارات على عملاتك${E.capped?` (بلا حدك اليومي ${E.wk})`:''} · الإشارات والتركيبات التي تمر: ${E.n}${E.cut>25?' · <span style="color:var(--amber)">⚠️ كثير — ارفع النسبة أو عدد المرات</span>':''}`}""",
     """function sgEstTxt(E){if(!E)return 'التقدير يظهر بعد بناء الدليل';
  return `بهذه النسبة كان سيصلك أسبوعياً نحو <b>${E.cut}</b> من الإشعارات على عملاتك${E.capped?` (بلا حدك اليومي ${E.wk})`:''}${E.cut>25?' · <span style="color:var(--amber)">⚠️ كثير — ارفع النسبة</span>':''}`}"""),
    ("""function sgEst(v){Object.assign(SGP,v);const lb=$('#sg_thr_v');if(lb&&v.thr!=null)lb.textContent=v.thr+'%';const lm=$('#sg_min_v');if(lm&&v.min!=null)lm.textContent=v.min;
  const lr=$('#sg_rmin_v');if(lr&&v.rmin!=null)lr.textContent=v.rmin;""",
     """function sgEst(v){Object.assign(SGP,v);const lb=$('#sg_thr_v');if(lb&&v.thr!=null)lb.textContent=v.thr+'%';"""),
    # 🔮 and the menu open the merged tab
    ("""  return `<button class="sg-go" onclick="openSig('now')">🎯 <b>الإشارات الآن</b>""",
     """  return `<button class="sg-go" onclick="openSig('ind')">🎯 <b>المؤشرات الآن</b>"""),
    ("""  if(k==='sig')return openSig('now');                            // 🎯 v3.36.66""",
     """  if(k==='sig')return openSig('ind');                            // 🎯 v3.36.66 · v3.36.71: «🎯 المؤشرات»"""),
    ("""    <div class="an-more"><button onclick="SGO['${gEsc(x.sym)}']=true;sgTab('now')">كل الإشارات الشغّالة ←</button></div></div>`}""",
     """    <div class="an-more"><button onclick="SGO['${gEsc(x.sym)}']=true;sgTab('ind')">🎯 كل مؤشرات العملة النشطة الآن ←</button></div></div>`}"""),
    ("""  const C=V.cat;if(!C)return sgHead(V)+'<div class="sg-empty">🏗️ الدليل لم يُبنَ بعد — تتابعه في «الآن»</div>';""",
     """  const C=V.cat;if(!C)return sgHead(V)+'<div class="sg-empty">🏗️ الدليل لم يُبنَ بعد — تتابعه في «🎯 المؤشرات»</div>';"""),
    ("""    for k, key in (("on", "sg_on"), ("rnd", "sg_rnd"), ("rare", "sg_rare")):""",
     """    for k, key in (("on", "sg_on"), ("rare", "sg_rare")):                     # 🎯 v3.36.71: «أفضل من العشوائي» ثابت بالداخل"""),
    ("""    for k, key, lo, hi in (("thr", "sg_thr", 50, 95), ("min", "sg_min", 3, 200), ("rmin", "sg_rmin", 3, 50), ("cap", "sg_cap", 0, 100)):""",
     """    for k, key, lo, hi in (("thr", "sg_thr", 50, 95), ("rmin", "sg_rmin", 3, 50), ("cap", "sg_cap", 0, 100)):     # «أقل عدد مرات» ثابت بالداخل"""),
    ("""    for k, lo, hi in (("thr", 50, 95), ("min", 3, 200), ("rmin", 3, 50), ("cap", 0, 100)):
        if v.get(k) is not None:
            try:
                c[k] = max(lo, min(hi, int(v[k])))
            except Exception:
                pass
    for k in ("rnd", "rare"):""",
     """    for k, lo, hi in (("thr", 50, 95), ("rmin", 3, 50), ("cap", 0, 100)):          # 🎯 v3.36.71: العدد والعشوائي ثابتان بالداخل
        if v.get(k) is not None:
            try:
                c[k] = max(lo, min(hi, int(v[k])))
            except Exception:
                pass
    for k in ("rare",):"""),
    ("""    <div class="mbtns"><button onclick="openSig()">🎯 الإشارات</button><button onclick="openGuide('','fc')">📖 الدليل</button>""",
     """    <div class="mbtns"><button onclick="openInd('ind')">🎯 المؤشرات</button><button onclick="openGuide('','fc')">📖 الدليل</button>"""),
    ("""     +L('🎯','الإشارات وإشعاراتها',"openSig('cfg')",'شراء · بيع · تجميع · صعود · نزول · السوق — بنسبتك'))}""",
     """     +L('🎯','المؤشرات وإشعارات المحلل',"openSig('cfg')",'شراء · بيع · تجميع · صعود · نزول · السوق — بنسبتك'))}"""),
    ('        msg = "↩️ عملات إشعارات الإشارات الآن نفس عملات الشريط"',
     '        msg = "↩️ عملات إشعارات المحلل الآن نفس عملات الشريط"'),
    ('placeholder="🔍 ابحث: MACD · بولنجر · Supertrend…"', 'placeholder="🔍 ابحث: الاتجاه · الدفع · القاع · MACD…"'),
    ("""<small>· الآن نفس عملات الشريط (📊) — أي تغيير هنا للإشارات فقط</small>""", """<small>· الآن نفس عملات الشريط (📊) — أي تغيير هنا لإشعارات المحلل فقط</small>"""),
    ("""APP_VERSION = "3.36.70\"""", """APP_VERSION = "3.36.71\""""),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    a = s.index("_SG_NM = {   # الأنظمة الـ36")
    b = s.index("_SG_OLDF = {")
    assert s.count("_SG_NM = {   # الأنظمة الـ36") == 1 and a < b
    s = s[:a] + NM + "\n" + s[b:]
    for i, (x, y) in enumerate(R):
        if s.count(x) != 1:
            print(f"❌ replacement {i}: found {s.count(x)} times — nothing written: {x[:100]!r}"); sys.exit(1)
        s = s.replace(x, y)
    # the old parts the merged tab replaces are removed (the owner's rule: update in place, nothing parallel)
    for x0, x1 in (("function sgCoin(x,V){const op=!!SGO[x.sym],F=x.fr||{};", "function sgCatUI(V){"),
                   ("async function indLoad(){clearTimeout(INDT);", "/* 🎯 v3.36.66: الإشارات — كل المؤشرات وتركيباتها")):
        if s.count(x0) != 1 or s.count(x1) != 1 or s.index(x0) > s.index(x1):
            print(f"❌ removal {x0[:40]!r} … {x1[:40]!r} not found once in order"); sys.exit(1)
        s = s[:s.index(x0)] + s[s.index(x1):]
    # the CSS of the merged tab
    css_a = ".sg-tabs{"
    if s.count(css_a) != 1:
        print(f"❌ css anchor found {s.count(css_a)} times"); sys.exit(1)
    s = s.replace(css_a, """.sg-pl{border-top:1px solid var(--bd);padding:6px 2px}.sg-pl .sg-plh{display:flex;gap:6px;align-items:center;flex-wrap:wrap}
.sg-pl .sg-plh b{color:var(--tx);font-size:13px}.sg-pl .sg-fr{margin-inline-start:auto}.sg-pl.ten{cursor:pointer}.sg-pl.flat{opacity:.75}
.sg-tech{color:var(--mut2);font-size:10.5px}.sg-grp{margin-top:8px}.ind-avg{margin-top:4px}
.sg-tabs{""", 1)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    import os
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R) + 2} replacements · 🎯 plain indicators · one tab · one setting · compiles · {p}")
