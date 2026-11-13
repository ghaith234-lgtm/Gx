.class public final Lcom/holy/dash/HolyWidget;
.super Landroid/appwidget/AppWidgetProvider;
.source "HolyWidget.java"


# static fields
.field static final ACT:Ljava/lang/String; = "com.holy.dash.WIDGET_REFRESH"

.field private static final BG:I = -0xdefefec

.field private static final DN:I = -0x10bab6

.field private static final LINE:I = 0x24ffffff

.field private static final MUT:I = -0x73736a

.field private static final TX:I = -0x1

.field private static final UP:I = -0xda58b0

.field private static volatile lastTick:J


# direct methods
.method static constructor <clinit>()V
    .registers 2

    .prologue
    .line 36
    const-wide/16 v0, 0x0

    sput-wide v0, Lcom/holy/dash/HolyWidget;->lastTick:J

    return-void
.end method

.method public constructor <init>()V
    .registers 1

    .prologue
    .line 34
    invoke-direct {p0}, Landroid/appwidget/AppWidgetProvider;-><init>()V

    return-void
.end method

.method static any(Landroid/content/Context;)Z
    .registers 2

    .prologue
    .line 67
    invoke-static {p0}, Lcom/holy/dash/HolyWidget;->count(Landroid/content/Context;)I

    move-result v0

    if-lez v0, :cond_8

    const/4 v0, 0x1

    :goto_7
    return v0

    :cond_8
    const/4 v0, 0x0

    goto :goto_7
.end method

.method static canPin(Landroid/content/Context;)Z
    .registers 4

    .prologue
    const/4 v1, 0x0

    .line 72
    sget v0, Landroid/os/Build$VERSION;->SDK_INT:I

    const/16 v2, 0x1a

    if-ge v0, v2, :cond_8

    .line 77
    :goto_7
    return v1

    .line 74
    :cond_8
    :try_start_8
    const-class v0, Landroid/appwidget/AppWidgetManager;

    invoke-virtual {p0, v0}, Landroid/content/Context;->getSystemService(Ljava/lang/Class;)Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Landroid/appwidget/AppWidgetManager;

    .line 75
    if-eqz v0, :cond_1b

    invoke-virtual {v0}, Landroid/appwidget/AppWidgetManager;->isRequestPinAppWidgetSupported()Z
    :try_end_15
    .catch Ljava/lang/Exception; {:try_start_8 .. :try_end_15} :catch_1d

    move-result v0

    if-eqz v0, :cond_1b

    const/4 v0, 0x1

    :goto_19
    move v1, v0

    goto :goto_7

    :cond_1b
    move v0, v1

    goto :goto_19

    .line 76
    :catch_1d
    move-exception v0

    goto :goto_7
.end method

.method private static col(Ljava/lang/String;)I
    .registers 2

    .prologue
    .line 176
    const-string v0, "u"

    invoke-virtual {v0, p0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_c

    const v0, -0xda58b0

    :goto_b
    return v0

    :cond_c
    const-string v0, "d"

    invoke-virtual {v0, p0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_18

    const v0, -0x10bab6

    goto :goto_b

    :cond_18
    const/4 v0, -0x1

    goto :goto_b
.end method

.method static count(Landroid/content/Context;)I
    .registers 4

    .prologue
    .line 60
    :try_start_0
    invoke-static {p0}, Landroid/appwidget/AppWidgetManager;->getInstance(Landroid/content/Context;)Landroid/appwidget/AppWidgetManager;

    move-result-object v0

    new-instance v1, Landroid/content/ComponentName;

    const-class v2, Lcom/holy/dash/HolyWidget;

    invoke-direct {v1, p0, v2}, Landroid/content/ComponentName;-><init>(Landroid/content/Context;Ljava/lang/Class;)V

    invoke-virtual {v0, v1}, Landroid/appwidget/AppWidgetManager;->getAppWidgetIds(Landroid/content/ComponentName;)[I

    move-result-object v0

    array-length v0, v0
    :try_end_10
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_10} :catch_11

    .line 62
    :goto_10
    return v0

    .line 61
    :catch_11
    move-exception v0

    .line 62
    const/4 v0, 0x0

    goto :goto_10
.end method

.method static draw(Landroid/content/Context;Ljava/lang/String;J)V
    .registers 22

    .prologue
    .line 130
    :try_start_0
    invoke-static/range {p0 .. p0}, Landroid/appwidget/AppWidgetManager;->getInstance(Landroid/content/Context;)Landroid/appwidget/AppWidgetManager;

    move-result-object v10

    .line 131
    new-instance v2, Landroid/content/ComponentName;

    const-class v3, Lcom/holy/dash/HolyWidget;

    move-object/from16 v0, p0

    invoke-direct {v2, v0, v3}, Landroid/content/ComponentName;-><init>(Landroid/content/Context;Ljava/lang/Class;)V

    invoke-virtual {v10, v2}, Landroid/appwidget/AppWidgetManager;->getAppWidgetIds(Landroid/content/ComponentName;)[I

    move-result-object v11

    .line 132
    array-length v2, v11
    :try_end_12
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_12} :catch_aa

    if-nez v2, :cond_15

    .line 158
    :cond_14
    :goto_14
    return-void

    .line 133
    :cond_15
    const/4 v2, 0x0

    .line 135
    if-eqz p1, :cond_25

    :try_start_18
    invoke-virtual/range {p1 .. p1}, Ljava/lang/String;->isEmpty()Z

    move-result v3

    if-nez v3, :cond_25

    new-instance v2, Lorg/json/JSONObject;

    move-object/from16 v0, p1

    invoke-direct {v2, v0}, Lorg/json/JSONObject;-><init>(Ljava/lang/String;)V
    :try_end_25
    .catch Ljava/lang/Exception; {:try_start_18 .. :try_end_25} :catch_97

    :cond_25
    move-object v3, v2

    .line 139
    :goto_26
    :try_start_26
    new-instance v2, Landroid/content/Intent;

    const-class v4, Lcom/holy/dash/MainActivity;

    move-object/from16 v0, p0

    invoke-direct {v2, v0, v4}, Landroid/content/Intent;-><init>(Landroid/content/Context;Ljava/lang/Class;)V

    .line 140
    const/high16 v4, 0x14000000

    invoke-virtual {v2, v4}, Landroid/content/Intent;->setFlags(I)Landroid/content/Intent;

    .line 141
    const/16 v4, 0x484f

    const/high16 v5, 0xc000000

    move-object/from16 v0, p0

    invoke-static {v0, v4, v2, v5}, Landroid/app/PendingIntent;->getActivity(Landroid/content/Context;ILandroid/content/Intent;I)Landroid/app/PendingIntent;

    move-result-object v12

    .line 142
    invoke-virtual/range {p0 .. p0}, Landroid/content/Context;->getResources()Landroid/content/res/Resources;

    move-result-object v2

    invoke-virtual {v2}, Landroid/content/res/Resources;->getDisplayMetrics()Landroid/util/DisplayMetrics;

    move-result-object v2

    iget v8, v2, Landroid/util/DisplayMetrics;->density:F

    .line 143
    array-length v13, v11

    const/4 v2, 0x0

    move v9, v2

    :goto_4b
    if-ge v9, v13, :cond_14

    aget v14, v11, v9

    .line 144
    invoke-virtual {v10, v14}, Landroid/appwidget/AppWidgetManager;->getAppWidgetOptions(I)Landroid/os/Bundle;

    move-result-object v2

    .line 145
    if-nez v2, :cond_9a

    const/4 v6, 0x0

    .line 146
    :goto_56
    if-nez v2, :cond_a2

    const/4 v7, 0x0

    .line 147
    :goto_59
    const/16 v2, 0xa0

    if-ge v6, v2, :cond_5f

    const/16 v6, 0x140

    .line 148
    :cond_5f
    const/16 v2, 0x5a

    if-ge v7, v2, :cond_65

    const/16 v7, 0xb4

    .line 149
    :cond_65
    new-instance v15, Landroid/widget/RemoteViews;

    invoke-virtual/range {p0 .. p0}, Landroid/content/Context;->getPackageName()Ljava/lang/String;

    move-result-object v2

    const/high16 v4, 0x7f050000

    invoke-direct {v15, v2, v4}, Landroid/widget/RemoteViews;-><init>(Ljava/lang/String;I)V

    .line 150
    const v16, 0x1020006

    move-object/from16 v2, p0

    move-wide/from16 v4, p2

    invoke-static/range {v2 .. v8}, Lcom/holy/dash/HolyWidget;->render(Landroid/content/Context;Lorg/json/JSONObject;JIIF)Landroid/graphics/Bitmap;

    move-result-object v2

    move/from16 v0, v16

    invoke-virtual {v15, v0, v2}, Landroid/widget/RemoteViews;->setImageViewBitmap(ILandroid/graphics/Bitmap;)V

    .line 151
    const v2, 0x1020006

    invoke-static {v3}, Lcom/holy/dash/HolyWidget;->speak(Lorg/json/JSONObject;)Ljava/lang/String;

    move-result-object v4

    invoke-virtual {v15, v2, v4}, Landroid/widget/RemoteViews;->setContentDescription(ILjava/lang/CharSequence;)V

    .line 152
    const v2, 0x1020006

    invoke-virtual {v15, v2, v12}, Landroid/widget/RemoteViews;->setOnClickPendingIntent(ILandroid/app/PendingIntent;)V

    .line 153
    invoke-virtual {v10, v14, v15}, Landroid/appwidget/AppWidgetManager;->updateAppWidget(ILandroid/widget/RemoteViews;)V

    .line 143
    add-int/lit8 v2, v9, 0x1

    move v9, v2

    goto :goto_4b

    .line 136
    :catch_97
    move-exception v2

    .line 137
    const/4 v3, 0x0

    goto :goto_26

    .line 145
    :cond_9a
    const-string v4, "appWidgetMinWidth"

    const/4 v5, 0x0

    invoke-virtual {v2, v4, v5}, Landroid/os/Bundle;->getInt(Ljava/lang/String;I)I

    move-result v6

    goto :goto_56

    .line 146
    :cond_a2
    const-string v4, "appWidgetMaxHeight"

    const/4 v5, 0x0

    invoke-virtual {v2, v4, v5}, Landroid/os/Bundle;->getInt(Ljava/lang/String;I)I
    :try_end_a8
    .catch Ljava/lang/Exception; {:try_start_26 .. :try_end_a8} :catch_aa

    move-result v7

    goto :goto_59

    .line 155
    :catch_aa
    move-exception v2

    goto/16 :goto_14
.end method

.method static fetch(Landroid/content/Context;)V
    .registers 9

    .prologue
    const-wide/16 v6, 0x0

    .line 110
    invoke-static {p0}, Lcom/holy/dash/HolyWidget;->store(Landroid/content/Context;)Landroid/content/SharedPreferences;

    move-result-object v0

    .line 111
    invoke-static {p0}, Lcom/holy/dash/Prefs;->origin(Landroid/content/Context;)Ljava/lang/String;

    move-result-object v1

    invoke-static {p0}, Lcom/holy/dash/Prefs;->token(Landroid/content/Context;)Ljava/lang/String;

    move-result-object v2

    .line 112
    invoke-virtual {v1}, Ljava/lang/String;->isEmpty()Z

    move-result v3

    if-nez v3, :cond_95

    invoke-virtual {v2}, Ljava/lang/String;->isEmpty()Z

    move-result v3

    if-nez v3, :cond_95

    .line 114
    :try_start_1a
    new-instance v3, Ljava/util/HashMap;

    invoke-direct {v3}, Ljava/util/HashMap;-><init>()V

    .line 115
    const-string v4, "X-Holy-Device"

    invoke-interface {v3, v4, v2}, Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;

    .line 116
    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v2, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    const-string v2, "/api/app/widget"

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    const/16 v2, 0x3a98

    const/4 v4, 0x1

    new-array v4, v4, [Ljava/net/HttpURLConnection;

    invoke-static {v1, v3, v2, v4}, Lcom/holy/dash/Net;->get(Ljava/lang/String;Ljava/util/Map;I[Ljava/net/HttpURLConnection;)Lcom/holy/dash/Net$Resp;

    move-result-object v1

    .line 117
    iget v2, v1, Lcom/holy/dash/Net$Resp;->code:I

    const/16 v3, 0xc8

    if-ne v2, v3, :cond_71

    invoke-interface {v0}, Landroid/content/SharedPreferences;->edit()Landroid/content/SharedPreferences$Editor;

    move-result-object v2

    const-string v3, "json"

    iget-object v1, v1, Lcom/holy/dash/Net$Resp;->body:Ljava/lang/String;

    invoke-interface {v2, v3, v1}, Landroid/content/SharedPreferences$Editor;->putString(Ljava/lang/String;Ljava/lang/String;)Landroid/content/SharedPreferences$Editor;

    move-result-object v1

    const-string v2, "ts"

    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v4

    invoke-interface {v1, v2, v4, v5}, Landroid/content/SharedPreferences$Editor;->putLong(Ljava/lang/String;J)Landroid/content/SharedPreferences$Editor;

    move-result-object v1

    invoke-interface {v1}, Landroid/content/SharedPreferences$Editor;->apply()V
    :try_end_5f
    .catch Ljava/lang/Exception; {:try_start_1a .. :try_end_5f} :catch_93

    .line 125
    :cond_5f
    :goto_5f
    const-string v1, "json"

    const-string v2, ""

    invoke-interface {v0, v1, v2}, Landroid/content/SharedPreferences;->getString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    const-string v2, "ts"

    invoke-interface {v0, v2, v6, v7}, Landroid/content/SharedPreferences;->getLong(Ljava/lang/String;J)J

    move-result-wide v2

    invoke-static {p0, v1, v2, v3}, Lcom/holy/dash/HolyWidget;->draw(Landroid/content/Context;Ljava/lang/String;J)V

    .line 126
    return-void

    .line 118
    :cond_71
    :try_start_71
    iget v2, v1, Lcom/holy/dash/Net$Resp;->code:I

    const/16 v3, 0x191

    if-eq v2, v3, :cond_7d

    iget v1, v1, Lcom/holy/dash/Net$Resp;->code:I

    const/16 v2, 0x193

    if-ne v1, v2, :cond_5f

    :cond_7d
    invoke-interface {v0}, Landroid/content/SharedPreferences;->edit()Landroid/content/SharedPreferences$Editor;

    move-result-object v1

    const-string v2, "json"

    invoke-interface {v1, v2}, Landroid/content/SharedPreferences$Editor;->remove(Ljava/lang/String;)Landroid/content/SharedPreferences$Editor;

    move-result-object v1

    const-string v2, "ts"

    const-wide/16 v4, 0x0

    invoke-interface {v1, v2, v4, v5}, Landroid/content/SharedPreferences$Editor;->putLong(Ljava/lang/String;J)Landroid/content/SharedPreferences$Editor;

    move-result-object v1

    invoke-interface {v1}, Landroid/content/SharedPreferences$Editor;->apply()V
    :try_end_92
    .catch Ljava/lang/Exception; {:try_start_71 .. :try_end_92} :catch_93

    goto :goto_5f

    .line 119
    :catch_93
    move-exception v1

    goto :goto_5f

    .line 123
    :cond_95
    invoke-interface {v0}, Landroid/content/SharedPreferences;->edit()Landroid/content/SharedPreferences$Editor;

    move-result-object v1

    const-string v2, "json"

    invoke-interface {v1, v2}, Landroid/content/SharedPreferences$Editor;->remove(Ljava/lang/String;)Landroid/content/SharedPreferences$Editor;

    move-result-object v1

    const-string v2, "ts"

    invoke-interface {v1, v2, v6, v7}, Landroid/content/SharedPreferences$Editor;->putLong(Ljava/lang/String;J)Landroid/content/SharedPreferences$Editor;

    move-result-object v1

    invoke-interface {v1}, Landroid/content/SharedPreferences$Editor;->apply()V

    goto :goto_5f
.end method

.method private static paint(FIZLandroid/graphics/Paint$Align;)Landroid/graphics/Paint;
    .registers 6

    .prologue
    .line 180
    new-instance v1, Landroid/graphics/Paint;

    const/16 v0, 0x81

    invoke-direct {v1, v0}, Landroid/graphics/Paint;-><init>(I)V

    .line 181
    invoke-virtual {v1, p0}, Landroid/graphics/Paint;->setTextSize(F)V

    .line 182
    invoke-virtual {v1, p1}, Landroid/graphics/Paint;->setColor(I)V

    .line 183
    if-eqz p2, :cond_18

    sget-object v0, Landroid/graphics/Typeface;->DEFAULT_BOLD:Landroid/graphics/Typeface;

    :goto_11
    invoke-virtual {v1, v0}, Landroid/graphics/Paint;->setTypeface(Landroid/graphics/Typeface;)Landroid/graphics/Typeface;

    .line 184
    invoke-virtual {v1, p3}, Landroid/graphics/Paint;->setTextAlign(Landroid/graphics/Paint$Align;)V

    .line 185
    return-object v1

    .line 183
    :cond_18
    sget-object v0, Landroid/graphics/Typeface;->DEFAULT:Landroid/graphics/Typeface;

    goto :goto_11
.end method

.method static pin(Landroid/content/Context;)Z
    .registers 6

    .prologue
    const/4 v1, 0x0

    .line 82
    invoke-static {p0}, Lcom/holy/dash/HolyWidget;->canPin(Landroid/content/Context;)Z

    move-result v0

    if-nez v0, :cond_9

    move v0, v1

    .line 86
    :goto_8
    return v0

    .line 84
    :cond_9
    :try_start_9
    const-class v0, Landroid/appwidget/AppWidgetManager;

    invoke-virtual {p0, v0}, Landroid/content/Context;->getSystemService(Ljava/lang/Class;)Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Landroid/appwidget/AppWidgetManager;

    new-instance v2, Landroid/content/ComponentName;

    const-class v3, Lcom/holy/dash/HolyWidget;

    invoke-direct {v2, p0, v3}, Landroid/content/ComponentName;-><init>(Landroid/content/Context;Ljava/lang/Class;)V

    const/4 v3, 0x0

    const/4 v4, 0x0

    invoke-virtual {v0, v2, v3, v4}, Landroid/appwidget/AppWidgetManager;->requestPinAppWidget(Landroid/content/ComponentName;Landroid/os/Bundle;Landroid/app/PendingIntent;)Z
    :try_end_1d
    .catch Ljava/lang/Exception; {:try_start_9 .. :try_end_1d} :catch_1f

    move-result v0

    goto :goto_8

    .line 85
    :catch_1f
    move-exception v0

    move v0, v1

    .line 86
    goto :goto_8
.end method

.method static refreshAsync(Landroid/content/Context;)V
    .registers 4

    .prologue
    .line 99
    invoke-virtual {p0}, Landroid/content/Context;->getApplicationContext()Landroid/content/Context;

    move-result-object v0

    .line 100
    invoke-static {v0}, Lcom/holy/dash/HolyWidget;->any(Landroid/content/Context;)Z

    move-result v1

    if-nez v1, :cond_b

    .line 107
    :goto_a
    return-void

    .line 101
    :cond_b
    new-instance v1, Ljava/lang/Thread;

    new-instance v2, Lcom/holy/dash/HolyWidget$1;

    invoke-direct {v2, v0}, Lcom/holy/dash/HolyWidget$1;-><init>(Landroid/content/Context;)V

    const-string v0, "holy-widget"

    invoke-direct {v1, v2, v0}, Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;Ljava/lang/String;)V

    .line 106
    invoke-virtual {v1}, Ljava/lang/Thread;->start()V

    goto :goto_a
.end method

.method static render(Landroid/content/Context;Lorg/json/JSONObject;JIIF)Landroid/graphics/Bitmap;
    .registers 8

    # app 2.0: the widget is drawn like the dashboard's card B in the interface's purple (WidgetArt.java)
    invoke-static/range {p0 .. p6}, Lcom/holy/dash/WidgetArt;->render(Landroid/content/Context;Lorg/json/JSONObject;JIIF)Landroid/graphics/Bitmap;

    move-result-object v0

    return-object v0
.end method

.method static speak(Lorg/json/JSONObject;)Ljava/lang/String;
    .registers 2

    invoke-static {p0}, Lcom/holy/dash/WidgetArt;->speak(Lorg/json/JSONObject;)Ljava/lang/String;

    move-result-object v0

    return-object v0
.end method

.method private static store(Landroid/content/Context;)Landroid/content/SharedPreferences;
    .registers 3

    .prologue
    .line 55
    const-string v0, "holy_widget"

    const/4 v1, 0x0

    invoke-virtual {p0, v0, v1}, Landroid/content/Context;->getSharedPreferences(Ljava/lang/String;I)Landroid/content/SharedPreferences;

    move-result-object v0

    return-object v0
.end method

.method private static text(Landroid/graphics/Canvas;Ljava/lang/String;FFFLandroid/graphics/Paint;)V
    .registers 8

    .prologue
    .line 190
    if-nez p1, :cond_4

    const-string p1, ""

    .line 191
    :cond_4
    invoke-virtual {p5}, Landroid/graphics/Paint;->getTextSize()F

    move-result v0

    .line 192
    :goto_8
    const/high16 v1, 0x40c00000    # 6.0f

    cmpl-float v1, v0, v1

    if-lez v1, :cond_1d

    invoke-virtual {p5, p1}, Landroid/graphics/Paint;->measureText(Ljava/lang/String;)F

    move-result v1

    cmpl-float v1, v1, p4

    if-lez v1, :cond_1d

    .line 193
    const/high16 v1, 0x3f000000    # 0.5f

    sub-float/2addr v0, v1

    .line 194
    invoke-virtual {p5, v0}, Landroid/graphics/Paint;->setTextSize(F)V

    goto :goto_8

    .line 196
    :cond_1d
    invoke-virtual {p0, p1, p2, p3, p5}, Landroid/graphics/Canvas;->drawText(Ljava/lang/String;FFLandroid/graphics/Paint;)V

    .line 197
    return-void
.end method

.method static tick(Landroid/content/Context;)V
    .registers 7

    .prologue
    .line 92
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v0

    .line 93
    sget-wide v2, Lcom/holy/dash/HolyWidget;->lastTick:J

    sub-long v2, v0, v2

    const-wide/32 v4, 0xea60

    cmp-long v2, v2, v4

    if-gez v2, :cond_10

    .line 96
    :cond_f
    :goto_f
    return-void

    .line 94
    :cond_10
    sput-wide v0, Lcom/holy/dash/HolyWidget;->lastTick:J

    .line 95
    invoke-static {p0}, Lcom/holy/dash/HolyWidget;->any(Landroid/content/Context;)Z

    move-result v0

    if-eqz v0, :cond_f

    invoke-static {p0}, Lcom/holy/dash/HolyWidget;->fetch(Landroid/content/Context;)V

    goto :goto_f
.end method


# virtual methods
.method public onAppWidgetOptionsChanged(Landroid/content/Context;Landroid/appwidget/AppWidgetManager;ILandroid/os/Bundle;)V
    .registers 11

    .prologue
    .line 45
    invoke-static {p1}, Lcom/holy/dash/HolyWidget;->store(Landroid/content/Context;)Landroid/content/SharedPreferences;

    move-result-object v0

    const-string v1, "json"

    const-string v2, ""

    invoke-interface {v0, v1, v2}, Landroid/content/SharedPreferences;->getString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    invoke-static {p1}, Lcom/holy/dash/HolyWidget;->store(Landroid/content/Context;)Landroid/content/SharedPreferences;

    move-result-object v1

    const-string v2, "ts"

    const-wide/16 v4, 0x0

    invoke-interface {v1, v2, v4, v5}, Landroid/content/SharedPreferences;->getLong(Ljava/lang/String;J)J

    move-result-wide v2

    invoke-static {p1, v0, v2, v3}, Lcom/holy/dash/HolyWidget;->draw(Landroid/content/Context;Ljava/lang/String;J)V

    .line 46
    return-void
.end method

.method public onReceive(Landroid/content/Context;Landroid/content/Intent;)V
    .registers 5

    .prologue
    .line 50
    invoke-super {p0, p1, p2}, Landroid/appwidget/AppWidgetProvider;->onReceive(Landroid/content/Context;Landroid/content/Intent;)V

    .line 51
    if-eqz p2, :cond_14

    const-string v0, "com.holy.dash.WIDGET_REFRESH"

    invoke-virtual {p2}, Landroid/content/Intent;->getAction()Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_14

    invoke-static {p1}, Lcom/holy/dash/HolyWidget;->refreshAsync(Landroid/content/Context;)V

    .line 52
    :cond_14
    return-void
.end method

.method public onUpdate(Landroid/content/Context;Landroid/appwidget/AppWidgetManager;[I)V
    .registers 4

    .prologue
    .line 40
    invoke-static {p1}, Lcom/holy/dash/HolyWidget;->refreshAsync(Landroid/content/Context;)V

    .line 41
    return-void
.end method
