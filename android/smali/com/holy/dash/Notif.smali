.class final Lcom/holy/dash/Notif;
.super Ljava/lang/Object;
.source "Notif.java"


# static fields
.field static final AMBER:I = -0x440dc

.field static final CH_ALERT:Ljava/lang/String; = "alert2"

.field static final CH_IND:Ljava/lang/String; = "ind"

.field static final CH_INFO:Ljava/lang/String; = "info"

.field static final CH_PRICE:Ljava/lang/String; = "price"

.field static final CH_TRADE:Ljava/lang/String; = "trade2"

.field static final CH_WATCH:Ljava/lang/String; = "watch"

.field static final CYAN:I = -0xdd2c12

.field static final GREEN:I = -0xcb2c67

.field static final ID_ITEM_BASE:I = 0x3e8

.field static final ID_SAVED_BASE:I = 0x7a120

.field static final ID_SUM_BASE:I = 0x384

.field static final ID_UNPAIRED:I = 0x2

.field static final ID_WATCH:I = 0x1

.field static final KINDS:[Ljava/lang/String;

.field static final OLD_CH:[Ljava/lang/String;

.field static final RED:I = -0x48e7b

.field static final VIOLET:I = -0x587406


# direct methods
.method static constructor <clinit>()V
    .registers 5

    .prologue
    const/4 v4, 0x2

    const/4 v3, 0x1

    const/4 v2, 0x0

    .line 30
    new-array v0, v4, [Ljava/lang/String;

    const-string v1, "trade"

    aput-object v1, v0, v2

    const-string v1, "alert"

    aput-object v1, v0, v3

    sput-object v0, Lcom/holy/dash/Notif;->OLD_CH:[Ljava/lang/String;

    .line 33
    const/4 v0, 0x5

    new-array v0, v0, [Ljava/lang/String;

    const-string v1, "trade"

    aput-object v1, v0, v2

    const-string v1, "alert"

    aput-object v1, v0, v3

    const-string v1, "info"

    aput-object v1, v0, v4

    const/4 v1, 0x3

    const-string v2, "price"

    aput-object v2, v0, v1

    const/4 v1, 0x4

    const-string v2, "ind"

    aput-object v2, v0, v1

    sput-object v0, Lcom/holy/dash/Notif;->KINDS:[Ljava/lang/String;

    return-void
.end method

.method private constructor <init>()V
    .registers 1

    .prologue
    .line 26
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method static builder(Landroid/content/Context;Ljava/lang/String;)Landroid/app/Notification$Builder;
    .registers 5

    .prologue
    const/16 v2, 0x1a

    .line 89
    sget v0, Landroid/os/Build$VERSION;->SDK_INT:I

    if-lt v0, v2, :cond_2f

    new-instance v0, Landroid/app/Notification$Builder;

    invoke-direct {v0, p0, p1}, Landroid/app/Notification$Builder;-><init>(Landroid/content/Context;Ljava/lang/String;)V

    .line 90
    :goto_b
    const v1, 0x7f030003

    invoke-virtual {v0, v1}, Landroid/app/Notification$Builder;->setSmallIcon(I)Landroid/app/Notification$Builder;

    .line 91
    sget v1, Landroid/os/Build$VERSION;->SDK_INT:I

    if-ge v1, v2, :cond_2e

    .line 92
    invoke-static {p1}, Lcom/holy/dash/Notif;->sounds(Ljava/lang/String;)Z

    move-result v1

    if-eqz v1, :cond_22

    invoke-static {p0}, Lcom/holy/dash/Notif;->tone(Landroid/content/Context;)Landroid/net/Uri;

    move-result-object v1

    invoke-virtual {v0, v1}, Landroid/app/Notification$Builder;->setSound(Landroid/net/Uri;)Landroid/app/Notification$Builder;

    .line 93
    :cond_22
    const-string v1, "alert2"

    invoke-virtual {v1, p1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v1

    if-eqz v1, :cond_35

    const/4 v1, 0x1

    :goto_2b
    invoke-virtual {v0, v1}, Landroid/app/Notification$Builder;->setPriority(I)Landroid/app/Notification$Builder;

    .line 96
    :cond_2e
    return-object v0

    .line 89
    :cond_2f
    new-instance v0, Landroid/app/Notification$Builder;

    invoke-direct {v0, p0}, Landroid/app/Notification$Builder;-><init>(Landroid/content/Context;)V

    goto :goto_b

    .line 93
    :cond_35
    const-string v1, "watch"

    invoke-virtual {v1, p1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v1

    if-eqz v1, :cond_3f

    const/4 v1, -0x2

    goto :goto_2b

    .line 94
    :cond_3f
    const-string v1, "info"

    invoke-virtual {v1, p1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v1

    if-eqz v1, :cond_49

    const/4 v1, -0x1

    goto :goto_2b

    :cond_49
    const/4 v1, 0x0

    goto :goto_2b
.end method

.method static channelOf(Ljava/lang/String;)Ljava/lang/String;
    .registers 2

    .prologue
    .line 125
    const-string v0, "alert"

    invoke-virtual {v0, p0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_b

    const-string v0, "alert2"

    :goto_a
    return-object v0

    :cond_b
    const-string v0, "trade"

    invoke-virtual {v0, p0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_16

    const-string v0, "trade2"

    goto :goto_a

    :cond_16
    const-string v0, "price"

    invoke-virtual {v0, p0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_21

    const-string v0, "price"

    goto :goto_a

    :cond_21
    const-string v0, "ind"

    invoke-virtual {v0, p0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_2c

    const-string v0, "ind"

    goto :goto_a

    :cond_2c
    const-string v0, "info"

    goto :goto_a
.end method

.method static channels(Landroid/content/Context;)V
    .registers 11

    .prologue
    const/4 v9, 0x4

    const/4 v8, 0x1

    const/4 v0, 0x0

    const/4 v7, 0x3

    .line 49
    sget v1, Landroid/os/Build$VERSION;->SDK_INT:I

    const/16 v2, 0x1a

    if-ge v1, v2, :cond_b

    .line 86
    :cond_a
    return-void

    .line 50
    :cond_b
    invoke-static {p0}, Lcom/holy/dash/Notif;->nm(Landroid/content/Context;)Landroid/app/NotificationManager;

    move-result-object v1

    .line 52
    new-instance v2, Landroid/app/NotificationChannel;

    const-string v3, "watch"

    const-string v4, "\ud83d\ude48 \u0633\u0637\u0631 \u0627\u0644\u0645\u0631\u0627\u0642\u0628\u0629 (\u064a\u0645\u0643\u0646\u0643 \u0625\u064a\u0642\u0627\u0641\u0647)"

    invoke-direct {v2, v3, v4, v8}, Landroid/app/NotificationChannel;-><init>(Ljava/lang/String;Ljava/lang/CharSequence;I)V

    .line 53
    const-string v3, "\u0627\u0644\u0633\u0637\u0631 \u0627\u0644\u0635\u063a\u064a\u0631 \u0627\u0644\u0630\u064a \u064a\u0628\u0642\u064a Holy \u064a\u0639\u0645\u0644 \u0641\u064a \u0627\u0644\u062e\u0644\u0641\u064a\u0629 \u2014 \u0625\u0630\u0627 \u0623\u0648\u0642\u0641\u062a\u0647 \u062a\u0628\u0642\u0649 \u0627\u0644\u0625\u0634\u0639\u0627\u0631\u0627\u062a \u062a\u0635\u0644 (\u0623\u0646\u062f\u0631\u0648\u064a\u062f 13 \u0648\u0623\u062d\u062f\u062b)"

    invoke-virtual {v2, v3}, Landroid/app/NotificationChannel;->setDescription(Ljava/lang/String;)V

    .line 54
    invoke-virtual {v2, v0}, Landroid/app/NotificationChannel;->setShowBadge(Z)V

    .line 55
    invoke-virtual {v1, v2}, Landroid/app/NotificationManager;->createNotificationChannel(Landroid/app/NotificationChannel;)V

    .line 56
    new-instance v2, Landroid/media/AudioAttributes$Builder;

    invoke-direct {v2}, Landroid/media/AudioAttributes$Builder;-><init>()V

    const/4 v3, 0x5

    invoke-virtual {v2, v3}, Landroid/media/AudioAttributes$Builder;->setUsage(I)Landroid/media/AudioAttributes$Builder;

    move-result-object v2

    .line 57
    invoke-virtual {v2, v9}, Landroid/media/AudioAttributes$Builder;->setContentType(I)Landroid/media/AudioAttributes$Builder;

    move-result-object v2

    invoke-virtual {v2}, Landroid/media/AudioAttributes$Builder;->build()Landroid/media/AudioAttributes;

    move-result-object v2

    .line 58
    invoke-static {p0}, Lcom/holy/dash/Notif;->tone(Landroid/content/Context;)Landroid/net/Uri;

    move-result-object v3

    .line 59
    new-instance v4, Landroid/app/NotificationChannel;

    const-string v5, "trade2"

    const-string v6, "\ud83d\udcb0 \u0627\u0644\u0635\u0641\u0642\u0627\u062a \u0648\u0627\u0644\u0623\u0631\u0628\u0627\u062d"

    invoke-direct {v4, v5, v6, v7}, Landroid/app/NotificationChannel;-><init>(Ljava/lang/String;Ljava/lang/CharSequence;I)V

    .line 60
    const-string v5, "\u0643\u0644 \u0631\u0628\u062d \u0648\u0635\u0641\u0642\u0629 \u0645\u0646 \u0628\u0648\u062a\u0627\u062a\u0643 \u2014 \u0628\u0646\u063a\u0645\u0629 Holy"

    invoke-virtual {v4, v5}, Landroid/app/NotificationChannel;->setDescription(Ljava/lang/String;)V

    .line 61
    invoke-virtual {v4, v3, v2}, Landroid/app/NotificationChannel;->setSound(Landroid/net/Uri;Landroid/media/AudioAttributes;)V

    .line 62
    invoke-virtual {v1, v4}, Landroid/app/NotificationManager;->createNotificationChannel(Landroid/app/NotificationChannel;)V

    .line 63
    new-instance v4, Landroid/app/NotificationChannel;

    const-string v5, "alert2"

    const-string v6, "\u26a0\ufe0f \u0627\u0644\u062a\u0646\u0628\u064a\u0647\u0627\u062a \u0627\u0644\u0645\u0647\u0645\u0629"

    invoke-direct {v4, v5, v6, v9}, Landroid/app/NotificationChannel;-><init>(Ljava/lang/String;Ljava/lang/CharSequence;I)V

    .line 64
    const-string v5, "\u0627\u0644\u062d\u0627\u0631\u0633 \u00b7 \u0627\u0644\u0631\u0642\u0627\u0628\u0629 \u00b7 \u0641\u0634\u0644 \u0627\u0644\u0623\u0648\u0627\u0645\u0631 \u00b7 \u0627\u0644\u0645\u064f\u0631\u0627\u0643\u0650\u0645 \u2014 \u0628\u0646\u063a\u0645\u0629 Holy"

    invoke-virtual {v4, v5}, Landroid/app/NotificationChannel;->setDescription(Ljava/lang/String;)V

    .line 65
    invoke-virtual {v4, v3, v2}, Landroid/app/NotificationChannel;->setSound(Landroid/net/Uri;Landroid/media/AudioAttributes;)V

    .line 66
    invoke-virtual {v4, v8}, Landroid/app/NotificationChannel;->enableVibration(Z)V

    .line 67
    invoke-virtual {v1, v4}, Landroid/app/NotificationManager;->createNotificationChannel(Landroid/app/NotificationChannel;)V

    .line 68
    new-instance v4, Landroid/app/NotificationChannel;

    const-string v5, "price"

    const-string v6, "\ud83d\udcc8 \u0625\u0634\u0639\u0627\u0631\u0627\u062a \u0627\u0644\u0623\u0633\u0639\u0627\u0631"

    invoke-direct {v4, v5, v6, v7}, Landroid/app/NotificationChannel;-><init>(Ljava/lang/String;Ljava/lang/CharSequence;I)V

    .line 69
    const-string v5, "\u0635\u0639\u0648\u062f \u0623\u0648 \u0647\u0628\u0648\u0637 \u0642\u0648\u064a \u0644\u0639\u0645\u0644\u0627\u062a \u0634\u0631\u064a\u0637 \u0627\u0644\u0623\u0633\u0639\u0627\u0631 \u2014 \u0628\u0646\u063a\u0645\u0629 Holy"

    invoke-virtual {v4, v5}, Landroid/app/NotificationChannel;->setDescription(Ljava/lang/String;)V

    .line 70
    invoke-virtual {v4, v3, v2}, Landroid/app/NotificationChannel;->setSound(Landroid/net/Uri;Landroid/media/AudioAttributes;)V

    .line 71
    invoke-virtual {v1, v4}, Landroid/app/NotificationManager;->createNotificationChannel(Landroid/app/NotificationChannel;)V

    .line 72
    new-instance v4, Landroid/app/NotificationChannel;

    const-string v5, "ind"

    const-string v6, "\ud83d\udcca \u062a\u0646\u0628\u064a\u0647\u0627\u062a \u0627\u0644\u0645\u0624\u0634\u0631\u0627\u062a"

    invoke-direct {v4, v5, v6, v7}, Landroid/app/NotificationChannel;-><init>(Ljava/lang/String;Ljava/lang/CharSequence;I)V

    .line 73
    const-string v5, "\u0642\u0628\u0644 \u0627\u0644\u062d\u0631\u0643\u0629: \u0627\u0644\u0645\u0624\u0634\u0631\u0627\u062a \u0627\u0646\u0642\u0644\u0628\u062a \u00b7 \u0627\u0646\u0636\u063a\u0627\u0637 \u00b7 \u0642\u0631\u0628 \u062f\u0639\u0645/\u0645\u0642\u0627\u0648\u0645\u0629 \u2014 \u0628\u0646\u063a\u0645\u0629 Holy \u00b7 \u0645\u0646\u0641\u0635\u0644\u0629 \u0639\u0646 \u0625\u0634\u0639\u0627\u0631\u0627\u062a \u0627\u0644\u0623\u0633\u0639\u0627\u0631"

    invoke-virtual {v4, v5}, Landroid/app/NotificationChannel;->setDescription(Ljava/lang/String;)V

    .line 74
    invoke-virtual {v4, v3, v2}, Landroid/app/NotificationChannel;->setSound(Landroid/net/Uri;Landroid/media/AudioAttributes;)V

    .line 75
    invoke-virtual {v1, v4}, Landroid/app/NotificationManager;->createNotificationChannel(Landroid/app/NotificationChannel;)V

    .line 76
    new-instance v2, Landroid/app/NotificationChannel;

    const-string v3, "info"

    const-string v4, "\u2139\ufe0f \u0645\u0639\u0644\u0648\u0645\u0627\u062a"

    const/4 v5, 0x2

    invoke-direct {v2, v3, v4, v5}, Landroid/app/NotificationChannel;-><init>(Ljava/lang/String;Ljava/lang/CharSequence;I)V

    .line 77
    const-string v3, "\u062a\u0634\u063a\u064a\u0644 \u0648\u0625\u064a\u0642\u0627\u0641 \u00b7 \u062a\u0642\u0627\u0631\u064a\u0631 \u00b7 \u062d\u0641\u0638 \u0627\u0644\u0645\u0644\u0641\u0627\u062a"

    invoke-virtual {v2, v3}, Landroid/app/NotificationChannel;->setDescription(Ljava/lang/String;)V

    .line 78
    invoke-virtual {v1, v2}, Landroid/app/NotificationManager;->createNotificationChannel(Landroid/app/NotificationChannel;)V

    .line 79
    sget-object v2, Lcom/holy/dash/Notif;->OLD_CH:[Ljava/lang/String;

    array-length v3, v2

    :goto_a1
    if-ge v0, v3, :cond_a

    aget-object v4, v2, v0

    .line 81
    :try_start_a5
    invoke-virtual {v1, v4}, Landroid/app/NotificationManager;->getNotificationChannel(Ljava/lang/String;)Landroid/app/NotificationChannel;

    move-result-object v5

    if-eqz v5, :cond_ae

    invoke-virtual {v1, v4}, Landroid/app/NotificationManager;->deleteNotificationChannel(Ljava/lang/String;)V
    :try_end_ae
    .catch Ljava/lang/Exception; {:try_start_a5 .. :try_end_ae} :catch_b1

    .line 79
    :cond_ae
    :goto_ae
    add-int/lit8 v0, v0, 0x1

    goto :goto_a1

    .line 82
    :catch_b1
    move-exception v4

    goto :goto_ae
.end method

.method static colorOf(Ljava/lang/String;)I
    .registers 2

    .prologue
    .line 129
    const-string v0, "alert"

    invoke-virtual {v0, p0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_c

    const v0, -0x48e7b

    :goto_b
    return v0

    :cond_c
    const-string v0, "trade"

    invoke-virtual {v0, p0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_18

    const v0, -0xcb2c67

    goto :goto_b

    :cond_18
    const-string v0, "price"

    invoke-virtual {v0, p0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_24

    const v0, -0xdd2c12

    goto :goto_b

    :cond_24
    const-string v0, "ind"

    invoke-virtual {v0, p0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_30

    const v0, -0x440dc

    goto :goto_b

    :cond_30
    const v0, -0x587406

    goto :goto_b
.end method

.method static money(D)Ljava/lang/String;
    .registers 10

    .prologue
    .line 137
    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    const-wide/16 v2, 0x0

    cmpl-double v0, p0, v2

    if-ltz v0, :cond_3c

    const-string v0, "+"

    :goto_d
    invoke-virtual {v1, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    sget-object v2, Ljava/util/Locale;->US:Ljava/util/Locale;

    invoke-static {p0, p1}, Ljava/lang/Math;->abs(D)D

    move-result-wide v4

    const-wide/high16 v6, 0x3ff0000000000000L    # 1.0

    cmpl-double v0, v4, v6

    if-ltz v0, :cond_3f

    const-string v0, "%.2f"

    :goto_1f
    const/4 v3, 0x1

    new-array v3, v3, [Ljava/lang/Object;

    const/4 v4, 0x0

    invoke-static {p0, p1}, Ljava/lang/Double;->valueOf(D)Ljava/lang/Double;

    move-result-object v5

    aput-object v5, v3, v4

    invoke-static {v2, v0, v3}, Ljava/lang/String;->format(Ljava/util/Locale;Ljava/lang/String;[Ljava/lang/Object;)Ljava/lang/String;

    move-result-object v0

    invoke-virtual {v1, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v1, "$"

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    return-object v0

    :cond_3c
    const-string v0, ""

    goto :goto_d

    :cond_3f
    const-string v0, "%.4f"

    goto :goto_1f
.end method

.method static nidOf(Lorg/json/JSONObject;)I
    .registers 5

    .prologue
    .line 167
    const-string v0, "id"

    const-wide/16 v2, 0x0

    invoke-virtual {p0, v0, v2, v3}, Lorg/json/JSONObject;->optLong(Ljava/lang/String;J)J

    move-result-wide v0

    const-wide/32 v2, 0x61a80

    rem-long/2addr v0, v2

    long-to-int v0, v0

    add-int/lit16 v0, v0, 0x3e8

    return v0
.end method

.method static nm(Landroid/content/Context;)Landroid/app/NotificationManager;
    .registers 2

    .prologue
    .line 36
    const-string v0, "notification"

    invoke-virtual {p0, v0}, Landroid/content/Context;->getSystemService(Ljava/lang/String;)Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Landroid/app/NotificationManager;

    return-object v0
.end method

.method static norm(Ljava/lang/String;)Ljava/lang/String;
    .registers 2

    .prologue
    .line 171
    const-string v0, "alert"

    invoke-virtual {v0, p0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-nez v0, :cond_20

    const-string v0, "trade"

    invoke-virtual {v0, p0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-nez v0, :cond_20

    const-string v0, "price"

    invoke-virtual {v0, p0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-nez v0, :cond_20

    const-string v0, "ind"

    invoke-virtual {v0, p0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_21

    :cond_20
    :goto_20
    return-object p0

    :cond_21
    const-string p0, "info"

    goto :goto_20
.end method

.method static open(Landroid/content/Context;Ljava/lang/String;I)Landroid/app/PendingIntent;
    .registers 5

    .prologue
    .line 100
    new-instance v0, Landroid/content/Intent;

    const-class v1, Lcom/holy/dash/MainActivity;

    invoke-direct {v0, p0, v1}, Landroid/content/Intent;-><init>(Landroid/content/Context;Ljava/lang/Class;)V

    .line 101
    const/high16 v1, 0x34000000

    invoke-virtual {v0, v1}, Landroid/content/Intent;->setFlags(I)Landroid/content/Intent;

    .line 102
    if-eqz p1, :cond_13

    const-string v1, "go"

    invoke-virtual {v0, v1, p1}, Landroid/content/Intent;->putExtra(Ljava/lang/String;Ljava/lang/String;)Landroid/content/Intent;

    .line 103
    :cond_13
    const/high16 v1, 0xc000000

    invoke-static {p0, p2, v0, v1}, Landroid/app/PendingIntent;->getActivity(Landroid/content/Context;ILandroid/content/Intent;I)Landroid/app/PendingIntent;

    move-result-object v0

    return-object v0
.end method

.method static post(Landroid/content/Context;Landroid/app/NotificationManager;Lorg/json/JSONObject;Z)V
    .registers 14

    .prologue
    .line 175
    const-string v0, "k"

    invoke-virtual {p2, v0}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    invoke-static {v0}, Lcom/holy/dash/Notif;->norm(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    .line 176
    const-string v0, "t"

    const-string v2, "Holy"

    invoke-virtual {p2, v0, v2}, Lorg/json/JSONObject;->optString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    .line 177
    const-string v2, "b"

    const-string v3, ""

    invoke-virtual {p2, v2, v3}, Lorg/json/JSONObject;->optString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    .line 178
    const-string v3, "id"

    const-wide/16 v4, 0x0

    invoke-virtual {p2, v3, v4, v5}, Lorg/json/JSONObject;->optLong(Ljava/lang/String;J)J

    move-result-wide v4

    .line 179
    invoke-static {p2}, Lcom/holy/dash/Notif;->nidOf(Lorg/json/JSONObject;)I

    move-result v3

    .line 180
    new-instance v6, Landroid/os/Bundle;

    invoke-direct {v6}, Landroid/os/Bundle;-><init>()V

    .line 181
    const-string v7, "holy_title"

    invoke-virtual {v6, v7, v0}, Landroid/os/Bundle;->putString(Ljava/lang/String;Ljava/lang/String;)V

    .line 182
    const-string v7, "holy_id"

    invoke-virtual {v6, v7, v4, v5}, Landroid/os/Bundle;->putLong(Ljava/lang/String;J)V

    .line 183
    const-string v4, "usd"

    invoke-virtual {p2, v4}, Lorg/json/JSONObject;->has(Ljava/lang/String;)Z

    move-result v4

    if-eqz v4, :cond_52

    const-string v4, "usd"

    invoke-virtual {p2, v4}, Lorg/json/JSONObject;->isNull(Ljava/lang/String;)Z

    move-result v4

    if-nez v4, :cond_52

    const-string v4, "holy_usd"

    const-string v5, "usd"

    const-wide/16 v8, 0x0

    invoke-virtual {p2, v5, v8, v9}, Lorg/json/JSONObject;->optDouble(Ljava/lang/String;D)D

    move-result-wide v8

    invoke-virtual {v6, v4, v8, v9}, Landroid/os/Bundle;->putDouble(Ljava/lang/String;D)V

    .line 184
    :cond_52
    invoke-static {v1}, Lcom/holy/dash/Notif;->channelOf(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v4

    invoke-static {p0, v4}, Lcom/holy/dash/Notif;->builder(Landroid/content/Context;Ljava/lang/String;)Landroid/app/Notification$Builder;

    move-result-object v4

    invoke-virtual {v4, v0}, Landroid/app/Notification$Builder;->setContentTitle(Ljava/lang/CharSequence;)Landroid/app/Notification$Builder;

    move-result-object v0

    invoke-virtual {v0, v2}, Landroid/app/Notification$Builder;->setContentText(Ljava/lang/CharSequence;)Landroid/app/Notification$Builder;

    move-result-object v0

    new-instance v4, Landroid/app/Notification$BigTextStyle;

    invoke-direct {v4}, Landroid/app/Notification$BigTextStyle;-><init>()V

    .line 185
    invoke-virtual {v4, v2}, Landroid/app/Notification$BigTextStyle;->bigText(Ljava/lang/CharSequence;)Landroid/app/Notification$BigTextStyle;

    move-result-object v2

    invoke-virtual {v0, v2}, Landroid/app/Notification$Builder;->setStyle(Landroid/app/Notification$Style;)Landroid/app/Notification$Builder;

    move-result-object v0

    invoke-static {v1}, Lcom/holy/dash/Notif;->colorOf(Ljava/lang/String;)I

    move-result v2

    invoke-virtual {v0, v2}, Landroid/app/Notification$Builder;->setColor(I)Landroid/app/Notification$Builder;

    move-result-object v0

    const-string v2, "ts"

    .line 186
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v4

    const-wide/16 v8, 0x3e8

    div-long/2addr v4, v8

    invoke-virtual {p2, v2, v4, v5}, Lorg/json/JSONObject;->optLong(Ljava/lang/String;J)J

    move-result-wide v4

    const-wide/16 v8, 0x3e8

    mul-long/2addr v4, v8

    invoke-virtual {v0, v4, v5}, Landroid/app/Notification$Builder;->setWhen(J)Landroid/app/Notification$Builder;

    move-result-object v0

    const/4 v2, 0x1

    invoke-virtual {v0, v2}, Landroid/app/Notification$Builder;->setShowWhen(Z)Landroid/app/Notification$Builder;

    move-result-object v0

    const/4 v2, 0x1

    invoke-virtual {v0, v2}, Landroid/app/Notification$Builder;->setAutoCancel(Z)Landroid/app/Notification$Builder;

    move-result-object v0

    const-string v2, "go"

    const-string v4, ""

    .line 187
    invoke-virtual {p2, v2, v4}, Lorg/json/JSONObject;->optString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    invoke-static {p0, v2, v3}, Lcom/holy/dash/Notif;->open(Landroid/content/Context;Ljava/lang/String;I)Landroid/app/PendingIntent;

    move-result-object v2

    invoke-virtual {v0, v2}, Landroid/app/Notification$Builder;->setContentIntent(Landroid/app/PendingIntent;)Landroid/app/Notification$Builder;

    move-result-object v0

    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    const-string v4, "holy_"

    invoke-virtual {v2, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v0, v2}, Landroid/app/Notification$Builder;->setGroup(Ljava/lang/String;)Landroid/app/Notification$Builder;

    move-result-object v0

    invoke-virtual {v0, v6}, Landroid/app/Notification$Builder;->addExtras(Landroid/os/Bundle;)Landroid/app/Notification$Builder;

    move-result-object v2

    .line 188
    const-string v0, "alert"

    invoke-virtual {v0, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_102

    const-string v0, "err"

    :goto_ca
    invoke-virtual {v2, v0}, Landroid/app/Notification$Builder;->setCategory(Ljava/lang/String;)Landroid/app/Notification$Builder;

    move-result-object v0

    .line 189
    if-eqz p3, :cond_105

    .line 190
    const/4 v2, 0x0

    invoke-virtual {v0, v2}, Landroid/app/Notification$Builder;->setVisibility(I)Landroid/app/Notification$Builder;

    move-result-object v2

    .line 191
    invoke-static {v1}, Lcom/holy/dash/Notif;->channelOf(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v4

    invoke-static {p0, v4}, Lcom/holy/dash/Notif;->builder(Landroid/content/Context;Ljava/lang/String;)Landroid/app/Notification$Builder;

    move-result-object v4

    const-string v5, "Holy"

    invoke-virtual {v4, v5}, Landroid/app/Notification$Builder;->setContentTitle(Ljava/lang/CharSequence;)Landroid/app/Notification$Builder;

    move-result-object v4

    invoke-static {v1}, Lcom/holy/dash/Notif;->publicText(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v5

    invoke-virtual {v4, v5}, Landroid/app/Notification$Builder;->setContentText(Ljava/lang/CharSequence;)Landroid/app/Notification$Builder;

    move-result-object v4

    invoke-static {v1}, Lcom/holy/dash/Notif;->colorOf(Ljava/lang/String;)I

    move-result v1

    invoke-virtual {v4, v1}, Landroid/app/Notification$Builder;->setColor(I)Landroid/app/Notification$Builder;

    move-result-object v1

    invoke-virtual {v1}, Landroid/app/Notification$Builder;->build()Landroid/app/Notification;

    move-result-object v1

    invoke-virtual {v2, v1}, Landroid/app/Notification$Builder;->setPublicVersion(Landroid/app/Notification;)Landroid/app/Notification$Builder;

    .line 195
    :goto_fa
    invoke-virtual {v0}, Landroid/app/Notification$Builder;->build()Landroid/app/Notification;

    move-result-object v0

    invoke-virtual {p1, v3, v0}, Landroid/app/NotificationManager;->notify(ILandroid/app/Notification;)V

    .line 196
    return-void

    .line 188
    :cond_102
    const-string v0, "status"

    goto :goto_ca

    .line 193
    :cond_105
    const/4 v1, 0x1

    invoke-virtual {v0, v1}, Landroid/app/Notification$Builder;->setVisibility(I)Landroid/app/Notification$Builder;

    goto :goto_fa
.end method

.method static publicText(Ljava/lang/String;)Ljava/lang/String;
    .registers 2

    .prologue
    .line 133
    const-string v0, "alert"

    invoke-virtual {v0, p0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_b

    const-string v0, "\u26a0\ufe0f \u062a\u0646\u0628\u064a\u0647 \u062c\u062f\u064a\u062f"

    :goto_a
    return-object v0

    :cond_b
    const-string v0, "trade"

    invoke-virtual {v0, p0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_16

    const-string v0, "\ud83d\udcb0 \u0635\u0641\u0642\u0629 \u062c\u062f\u064a\u062f\u0629"

    goto :goto_a

    :cond_16
    const-string v0, "price"

    invoke-virtual {v0, p0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_21

    const-string v0, "\ud83d\udcc8 \u0625\u0634\u0639\u0627\u0631 \u0633\u0639\u0631"

    goto :goto_a

    :cond_21
    const-string v0, "ind"

    invoke-virtual {v0, p0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_2c

    const-string v0, "\ud83d\udcca \u062a\u0646\u0628\u064a\u0647 \u0645\u0624\u0634\u0631\u0627\u062a"

    goto :goto_a

    :cond_2c
    const-string v0, "\u2139\ufe0f \u0625\u0634\u0639\u0627\u0631 \u062c\u062f\u064a\u062f"

    goto :goto_a
.end method

.method static saved(Landroid/content/Context;Ljava/lang/String;Landroid/net/Uri;Ljava/lang/String;)V
    .registers 10

    .prologue
    .line 250
    const v0, 0x7a120

    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v2

    const-wide/32 v4, 0x186a0

    rem-long/2addr v2, v4

    long-to-int v1, v2

    add-int/2addr v0, v1

    .line 251
    const-string v1, "info"

    invoke-static {p0, v1}, Lcom/holy/dash/Notif;->builder(Landroid/content/Context;Ljava/lang/String;)Landroid/app/Notification$Builder;

    move-result-object v1

    const-string v2, "\u2b07\ufe0f \u062d\u064f\u0641\u0638 \u0641\u064a \u0627\u0644\u062a\u0646\u0632\u064a\u0644\u0627\u062a"

    invoke-virtual {v1, v2}, Landroid/app/Notification$Builder;->setContentTitle(Ljava/lang/CharSequence;)Landroid/app/Notification$Builder;

    move-result-object v1

    invoke-virtual {v1, p1}, Landroid/app/Notification$Builder;->setContentText(Ljava/lang/CharSequence;)Landroid/app/Notification$Builder;

    move-result-object v1

    const v2, -0xdd2c12

    invoke-virtual {v1, v2}, Landroid/app/Notification$Builder;->setColor(I)Landroid/app/Notification$Builder;

    move-result-object v1

    const/4 v2, 0x1

    invoke-virtual {v1, v2}, Landroid/app/Notification$Builder;->setAutoCancel(Z)Landroid/app/Notification$Builder;

    move-result-object v1

    .line 252
    if-eqz p2, :cond_50

    .line 253
    new-instance v2, Landroid/content/Intent;

    const-string v3, "android.intent.action.VIEW"

    invoke-direct {v2, v3}, Landroid/content/Intent;-><init>(Ljava/lang/String;)V

    invoke-virtual {v2, p2, p3}, Landroid/content/Intent;->setDataAndType(Landroid/net/Uri;Ljava/lang/String;)Landroid/content/Intent;

    move-result-object v2

    const v3, 0x10000001

    invoke-virtual {v2, v3}, Landroid/content/Intent;->addFlags(I)Landroid/content/Intent;

    move-result-object v2

    .line 254
    invoke-static {v2, p1}, Landroid/content/Intent;->createChooser(Landroid/content/Intent;Ljava/lang/CharSequence;)Landroid/content/Intent;

    move-result-object v2

    const/high16 v3, 0x10000000

    invoke-virtual {v2, v3}, Landroid/content/Intent;->addFlags(I)Landroid/content/Intent;

    move-result-object v2

    const/high16 v3, 0xc000000

    invoke-static {p0, v0, v2, v3}, Landroid/app/PendingIntent;->getActivity(Landroid/content/Context;ILandroid/content/Intent;I)Landroid/app/PendingIntent;

    move-result-object v2

    invoke-virtual {v1, v2}, Landroid/app/Notification$Builder;->setContentIntent(Landroid/app/PendingIntent;)Landroid/app/Notification$Builder;

    .line 257
    :cond_50
    invoke-static {p0}, Lcom/holy/dash/Notif;->nm(Landroid/content/Context;)Landroid/app/NotificationManager;

    move-result-object v2

    invoke-virtual {v1}, Landroid/app/Notification$Builder;->build()Landroid/app/Notification;

    move-result-object v1

    invoke-virtual {v2, v0, v1}, Landroid/app/NotificationManager;->notify(ILandroid/app/Notification;)V

    .line 258
    return-void
.end method

.method static show(Landroid/content/Context;Lorg/json/JSONArray;)V
    .registers 13

    .prologue
    const/4 v1, 0x0

    .line 142
    if-eqz p1, :cond_9

    invoke-virtual {p1}, Lorg/json/JSONArray;->length()I

    move-result v0

    if-nez v0, :cond_a

    .line 164
    :cond_9
    return-void

    .line 143
    :cond_a
    invoke-static {p0}, Lcom/holy/dash/Notif;->nm(Landroid/content/Context;)Landroid/app/NotificationManager;

    move-result-object v6

    .line 144
    invoke-static {p0}, Lcom/holy/dash/Prefs;->hideOnLock(Landroid/content/Context;)Z

    move-result v7

    .line 145
    new-instance v8, Ljava/util/ArrayList;

    invoke-direct {v8}, Ljava/util/ArrayList;-><init>()V

    move v0, v1

    .line 146
    :goto_18
    invoke-virtual {p1}, Lorg/json/JSONArray;->length()I

    move-result v2

    if-ge v0, v2, :cond_2a

    .line 147
    invoke-virtual {p1, v0}, Lorg/json/JSONArray;->optJSONObject(I)Lorg/json/JSONObject;

    move-result-object v2

    .line 148
    if-eqz v2, :cond_27

    invoke-interface {v8, v2}, Ljava/util/List;->add(Ljava/lang/Object;)Z

    .line 146
    :cond_27
    add-int/lit8 v0, v0, 0x1

    goto :goto_18

    .line 150
    :cond_2a
    invoke-interface {v8}, Ljava/util/List;->size()I

    move-result v0

    const/4 v2, 0x6

    if-le v0, v2, :cond_66

    const/4 v0, 0x1

    move v2, v0

    :goto_33
    move v3, v1

    .line 151
    :goto_34
    sget-object v0, Lcom/holy/dash/Notif;->KINDS:[Ljava/lang/String;

    array-length v0, v0

    if-ge v3, v0, :cond_9

    .line 152
    sget-object v0, Lcom/holy/dash/Notif;->KINDS:[Ljava/lang/String;

    aget-object v4, v0, v3

    .line 153
    new-instance v9, Ljava/util/ArrayList;

    invoke-direct {v9}, Ljava/util/ArrayList;-><init>()V

    .line 154
    invoke-interface {v8}, Ljava/util/List;->iterator()Ljava/util/Iterator;

    move-result-object v5

    :cond_46
    :goto_46
    invoke-interface {v5}, Ljava/util/Iterator;->hasNext()Z

    move-result v0

    if-eqz v0, :cond_68

    invoke-interface {v5}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Lorg/json/JSONObject;

    const-string v10, "k"

    invoke-virtual {v0, v10}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v10

    invoke-static {v10}, Lcom/holy/dash/Notif;->norm(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v10

    invoke-virtual {v4, v10}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v10

    if-eqz v10, :cond_46

    invoke-interface {v9, v0}, Ljava/util/List;->add(Ljava/lang/Object;)Z

    goto :goto_46

    :cond_66
    move v2, v1

    .line 150
    goto :goto_33

    .line 155
    :cond_68
    invoke-interface {v9}, Ljava/util/List;->isEmpty()Z

    move-result v0

    if-eqz v0, :cond_72

    .line 151
    :goto_6e
    add-int/lit8 v0, v3, 0x1

    move v3, v0

    goto :goto_34

    .line 156
    :cond_72
    new-instance v10, Ljava/util/HashSet;

    invoke-direct {v10}, Ljava/util/HashSet;-><init>()V

    .line 157
    if-eqz v2, :cond_ab

    invoke-interface {v9}, Ljava/util/List;->size()I

    move-result v0

    add-int/lit8 v0, v0, -0x2

    invoke-static {v1, v0}, Ljava/lang/Math;->max(II)I

    move-result v0

    move v4, v0

    :goto_84
    move v5, v1

    .line 158
    :goto_85
    invoke-interface {v9}, Ljava/util/List;->size()I

    move-result v0

    if-ge v5, v0, :cond_ad

    .line 159
    invoke-interface {v9, v5}, Ljava/util/List;->get(I)Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Lorg/json/JSONObject;

    invoke-static {v0}, Lcom/holy/dash/Notif;->nidOf(Lorg/json/JSONObject;)I

    move-result v0

    invoke-static {v0}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;

    move-result-object v0

    invoke-interface {v10, v0}, Ljava/util/Set;->add(Ljava/lang/Object;)Z

    .line 160
    if-lt v5, v4, :cond_a7

    invoke-interface {v9, v5}, Ljava/util/List;->get(I)Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Lorg/json/JSONObject;

    invoke-static {p0, v6, v0, v7}, Lcom/holy/dash/Notif;->post(Landroid/content/Context;Landroid/app/NotificationManager;Lorg/json/JSONObject;Z)V

    .line 158
    :cond_a7
    add-int/lit8 v0, v5, 0x1

    move v5, v0

    goto :goto_85

    :cond_ab
    move v4, v1

    .line 157
    goto :goto_84

    .line 162
    :cond_ad
    invoke-static {p0, v6, v3, v9, v10}, Lcom/holy/dash/Notif;->summary(Landroid/content/Context;Landroid/app/NotificationManager;ILjava/util/List;Ljava/util/Set;)V

    goto :goto_6e
.end method

.method static sounds(Ljava/lang/String;)Z
    .registers 2

    .prologue
    .line 45
    const-string v0, "trade2"

    invoke-virtual {v0, p0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-nez v0, :cond_20

    const-string v0, "alert2"

    invoke-virtual {v0, p0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-nez v0, :cond_20

    const-string v0, "price"

    invoke-virtual {v0, p0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-nez v0, :cond_20

    const-string v0, "ind"

    invoke-virtual {v0, p0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_22

    :cond_20
    const/4 v0, 0x1

    :goto_21
    return v0

    :cond_22
    const/4 v0, 0x0

    goto :goto_21
.end method

.method static summary(Landroid/content/Context;Landroid/app/NotificationManager;ILjava/util/List;Ljava/util/Set;)V
    .registers 21
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Landroid/content/Context;",
            "Landroid/app/NotificationManager;",
            "I",
            "Ljava/util/List",
            "<",
            "Lorg/json/JSONObject;",
            ">;",
            "Ljava/util/Set",
            "<",
            "Ljava/lang/Integer;",
            ">;)V"
        }
    .end annotation

    .prologue
    .line 200
    sget-object v2, Lcom/holy/dash/Notif;->KINDS:[Ljava/lang/String;

    aget-object v9, v2, p2

    .line 201
    const/4 v3, 0x0

    .line 202
    const-wide/16 v4, 0x0

    .line 203
    const/4 v2, 0x0

    .line 204
    new-instance v10, Ljava/util/ArrayList;

    invoke-direct {v10}, Ljava/util/ArrayList;-><init>()V

    .line 205
    new-instance v11, Ljava/util/ArrayList;

    invoke-direct {v11}, Ljava/util/ArrayList;-><init>()V

    .line 207
    :try_start_12
    invoke-virtual/range {p1 .. p1}, Landroid/app/NotificationManager;->getActiveNotifications()[Landroid/service/notification/StatusBarNotification;

    move-result-object v7

    array-length v8, v7

    const/4 v6, 0x0

    :goto_18
    if-ge v6, v8, :cond_7b

    aget-object v12, v7, v6

    .line 208
    invoke-virtual {v12}, Landroid/service/notification/StatusBarNotification;->getNotification()Landroid/app/Notification;

    move-result-object v13

    .line 209
    new-instance v14, Ljava/lang/StringBuilder;

    invoke-direct {v14}, Ljava/lang/StringBuilder;-><init>()V

    const-string v15, "holy_"

    invoke-virtual {v14, v15}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v14

    invoke-virtual {v14, v9}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v14

    invoke-virtual {v14}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v14

    invoke-virtual {v13}, Landroid/app/Notification;->getGroup()Ljava/lang/String;

    move-result-object v15

    invoke-virtual {v14, v15}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v14

    if-eqz v14, :cond_53

    iget v14, v13, Landroid/app/Notification;->flags:I

    and-int/lit16 v14, v14, 0x200

    if-nez v14, :cond_53

    invoke-virtual {v12}, Landroid/service/notification/StatusBarNotification;->getId()I

    move-result v12

    invoke-static {v12}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;

    move-result-object v12

    move-object/from16 v0, p4

    invoke-interface {v0, v12}, Ljava/util/Set;->contains(Ljava/lang/Object;)Z

    move-result v12

    if-eqz v12, :cond_56

    .line 207
    :cond_53
    :goto_53
    add-int/lit8 v6, v6, 0x1

    goto :goto_18

    .line 210
    :cond_56
    add-int/lit8 v3, v3, 0x1

    .line 211
    iget-object v12, v13, Landroid/app/Notification;->extras:Landroid/os/Bundle;

    const-string v14, "holy_usd"

    invoke-virtual {v12, v14}, Landroid/os/Bundle;->containsKey(Ljava/lang/String;)Z

    move-result v12

    if-eqz v12, :cond_6c

    iget-object v12, v13, Landroid/app/Notification;->extras:Landroid/os/Bundle;

    const-string v14, "holy_usd"

    invoke-virtual {v12, v14}, Landroid/os/Bundle;->getDouble(Ljava/lang/String;)D

    move-result-wide v14

    add-double/2addr v4, v14

    const/4 v2, 0x1

    .line 212
    :cond_6c
    iget-object v12, v13, Landroid/app/Notification;->extras:Landroid/os/Bundle;

    const-string v13, "holy_title"

    invoke-virtual {v12, v13}, Landroid/os/Bundle;->getString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v12

    .line 213
    if-eqz v12, :cond_53

    invoke-interface {v11, v12}, Ljava/util/List;->add(Ljava/lang/Object;)Z
    :try_end_79
    .catch Ljava/lang/Exception; {:try_start_12 .. :try_end_79} :catch_7a

    goto :goto_53

    .line 215
    :catch_7a
    move-exception v6

    .line 218
    :cond_7b
    invoke-interface/range {p3 .. p3}, Ljava/util/List;->size()I

    move-result v6

    add-int/lit8 v7, v6, -0x1

    move v6, v2

    move v8, v3

    :goto_83
    if-ltz v7, :cond_be

    .line 219
    move-object/from16 v0, p3

    invoke-interface {v0, v7}, Ljava/util/List;->get(I)Ljava/lang/Object;

    move-result-object v2

    check-cast v2, Lorg/json/JSONObject;

    .line 220
    add-int/lit8 v8, v8, 0x1

    .line 221
    const-string v3, "usd"

    invoke-virtual {v2, v3}, Lorg/json/JSONObject;->has(Ljava/lang/String;)Z

    move-result v3

    if-eqz v3, :cond_260

    const-string v3, "usd"

    invoke-virtual {v2, v3}, Lorg/json/JSONObject;->isNull(Ljava/lang/String;)Z

    move-result v3

    if-nez v3, :cond_260

    const-string v3, "usd"

    const-wide/16 v12, 0x0

    invoke-virtual {v2, v3, v12, v13}, Lorg/json/JSONObject;->optDouble(Ljava/lang/String;D)D

    move-result-wide v12

    add-double/2addr v4, v12

    const/4 v3, 0x1

    .line 222
    :goto_a9
    invoke-interface {v10}, Ljava/util/List;->size()I

    move-result v6

    const/4 v12, 0x6

    if-ge v6, v12, :cond_b9

    const-string v6, "t"

    invoke-virtual {v2, v6}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    invoke-interface {v10, v2}, Ljava/util/List;->add(Ljava/lang/Object;)Z

    .line 218
    :cond_b9
    add-int/lit8 v2, v7, -0x1

    move v7, v2

    move v6, v3

    goto :goto_83

    .line 224
    :cond_be
    invoke-interface {v11}, Ljava/util/List;->iterator()Ljava/util/Iterator;

    move-result-object v3

    :cond_c2
    :goto_c2
    invoke-interface {v3}, Ljava/util/Iterator;->hasNext()Z

    move-result v2

    if-eqz v2, :cond_d9

    invoke-interface {v3}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v2

    check-cast v2, Ljava/lang/String;

    invoke-interface {v10}, Ljava/util/List;->size()I

    move-result v7

    const/4 v11, 0x6

    if-ge v7, v11, :cond_c2

    invoke-interface {v10, v2}, Ljava/util/List;->add(Ljava/lang/Object;)Z

    goto :goto_c2

    .line 225
    :cond_d9
    move/from16 v0, p2

    add-int/lit16 v7, v0, 0x384

    .line 226
    const/4 v2, 0x2

    if-ge v8, v2, :cond_e6

    .line 227
    move-object/from16 v0, p1

    invoke-virtual {v0, v7}, Landroid/app/NotificationManager;->cancel(I)V

    .line 241
    :goto_e5
    return-void

    .line 230
    :cond_e6
    const-string v2, "trade"

    invoke-virtual {v2, v9}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v2

    if-eqz v2, :cond_145

    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    const-string v3, "\ud83d\udcb0 "

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2, v8}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v2

    const-string v3, " \u0635\u0641\u0642\u0627\u062a"

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    if-eqz v6, :cond_142

    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    const-string v6, " \u00b7 "

    invoke-virtual {v2, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-static {v4, v5}, Lcom/holy/dash/Notif;->money(D)Ljava/lang/String;

    move-result-object v4

    invoke-virtual {v2, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    :goto_11c
    invoke-virtual {v3, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    move-object v3, v2

    .line 233
    :goto_125
    new-instance v2, Landroid/app/Notification$InboxStyle;

    invoke-direct {v2}, Landroid/app/Notification$InboxStyle;-><init>()V

    invoke-virtual {v2, v3}, Landroid/app/Notification$InboxStyle;->setBigContentTitle(Ljava/lang/CharSequence;)Landroid/app/Notification$InboxStyle;

    move-result-object v4

    .line 234
    invoke-interface {v10}, Ljava/util/List;->iterator()Ljava/util/Iterator;

    move-result-object v5

    :goto_132
    invoke-interface {v5}, Ljava/util/Iterator;->hasNext()Z

    move-result v2

    if-eqz v2, :cond_1cb

    invoke-interface {v5}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v2

    check-cast v2, Ljava/lang/String;

    invoke-virtual {v4, v2}, Landroid/app/Notification$InboxStyle;->addLine(Ljava/lang/CharSequence;)Landroid/app/Notification$InboxStyle;

    goto :goto_132

    .line 230
    :cond_142
    const-string v2, ""

    goto :goto_11c

    .line 231
    :cond_145
    const-string v2, "alert"

    invoke-virtual {v2, v9}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v2

    if-eqz v2, :cond_168

    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    const-string v3, "\u26a0\ufe0f "

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2, v8}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v2

    const-string v3, " \u062a\u0646\u0628\u064a\u0647\u0627\u062a"

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    move-object v3, v2

    goto :goto_125

    :cond_168
    const-string v2, "price"

    invoke-virtual {v2, v9}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v2

    if-eqz v2, :cond_18b

    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    const-string v3, "\ud83d\udcc8 "

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2, v8}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v2

    const-string v3, " \u0625\u0634\u0639\u0627\u0631\u0627\u062a \u0623\u0633\u0639\u0627\u0631"

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    move-object v3, v2

    goto :goto_125

    .line 232
    :cond_18b
    const-string v2, "ind"

    invoke-virtual {v2, v9}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v2

    if-eqz v2, :cond_1af

    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    const-string v3, "\ud83d\udcca "

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2, v8}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v2

    const-string v3, " \u062a\u0646\u0628\u064a\u0647\u0627\u062a \u0645\u0624\u0634\u0631\u0627\u062a"

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    move-object v3, v2

    goto/16 :goto_125

    :cond_1af
    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    const-string v3, "\u2139\ufe0f "

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2, v8}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v2

    const-string v3, " \u0625\u0634\u0639\u0627\u0631\u0627\u062a"

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    move-object v3, v2

    goto/16 :goto_125

    .line 235
    :cond_1cb
    invoke-static {v9}, Lcom/holy/dash/Notif;->channelOf(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    move-object/from16 v0, p0

    invoke-static {v0, v2}, Lcom/holy/dash/Notif;->builder(Landroid/content/Context;Ljava/lang/String;)Landroid/app/Notification$Builder;

    move-result-object v2

    invoke-virtual {v2, v3}, Landroid/app/Notification$Builder;->setContentTitle(Ljava/lang/CharSequence;)Landroid/app/Notification$Builder;

    move-result-object v3

    invoke-interface {v10}, Ljava/util/List;->isEmpty()Z

    move-result v2

    if-eqz v2, :cond_24a

    const-string v2, ""

    :goto_1e1
    invoke-virtual {v3, v2}, Landroid/app/Notification$Builder;->setContentText(Ljava/lang/CharSequence;)Landroid/app/Notification$Builder;

    move-result-object v2

    .line 236
    invoke-virtual {v2, v4}, Landroid/app/Notification$Builder;->setStyle(Landroid/app/Notification$Style;)Landroid/app/Notification$Builder;

    move-result-object v2

    invoke-static {v9}, Lcom/holy/dash/Notif;->colorOf(Ljava/lang/String;)I

    move-result v3

    invoke-virtual {v2, v3}, Landroid/app/Notification$Builder;->setColor(I)Landroid/app/Notification$Builder;

    move-result-object v2

    new-instance v3, Ljava/lang/StringBuilder;

    invoke-direct {v3}, Ljava/lang/StringBuilder;-><init>()V

    const-string v4, "holy_"

    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3, v9}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v2, v3}, Landroid/app/Notification$Builder;->setGroup(Ljava/lang/String;)Landroid/app/Notification$Builder;

    move-result-object v2

    const/4 v3, 0x1

    invoke-virtual {v2, v3}, Landroid/app/Notification$Builder;->setGroupSummary(Z)Landroid/app/Notification$Builder;

    move-result-object v2

    const/4 v3, 0x1

    invoke-virtual {v2, v3}, Landroid/app/Notification$Builder;->setAutoCancel(Z)Landroid/app/Notification$Builder;

    move-result-object v2

    const/4 v3, 0x1

    .line 237
    invoke-virtual {v2, v3}, Landroid/app/Notification$Builder;->setOnlyAlertOnce(Z)Landroid/app/Notification$Builder;

    move-result-object v3

    const-string v2, "trade"

    invoke-virtual {v2, v9}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v2

    if-eqz v2, :cond_252

    const-string v2, "reports"

    :goto_221
    move-object/from16 v0, p0

    invoke-static {v0, v2, v7}, Lcom/holy/dash/Notif;->open(Landroid/content/Context;Ljava/lang/String;I)Landroid/app/PendingIntent;

    move-result-object v2

    invoke-virtual {v3, v2}, Landroid/app/Notification$Builder;->setContentIntent(Landroid/app/PendingIntent;)Landroid/app/Notification$Builder;

    move-result-object v2

    .line 238
    sget v3, Landroid/os/Build$VERSION;->SDK_INT:I

    const/16 v4, 0x1a

    if-lt v3, v4, :cond_235

    const/4 v3, 0x2

    invoke-virtual {v2, v3}, Landroid/app/Notification$Builder;->setGroupAlertBehavior(I)Landroid/app/Notification$Builder;

    .line 239
    :cond_235
    invoke-static/range {p0 .. p0}, Lcom/holy/dash/Prefs;->hideOnLock(Landroid/content/Context;)Z

    move-result v3

    if-eqz v3, :cond_23f

    const/4 v3, 0x0

    invoke-virtual {v2, v3}, Landroid/app/Notification$Builder;->setVisibility(I)Landroid/app/Notification$Builder;

    .line 240
    :cond_23f
    invoke-virtual {v2}, Landroid/app/Notification$Builder;->build()Landroid/app/Notification;

    move-result-object v2

    move-object/from16 v0, p1

    invoke-virtual {v0, v7, v2}, Landroid/app/NotificationManager;->notify(ILandroid/app/Notification;)V

    goto/16 :goto_e5

    .line 235
    :cond_24a
    const/4 v2, 0x0

    invoke-interface {v10, v2}, Ljava/util/List;->get(I)Ljava/lang/Object;

    move-result-object v2

    check-cast v2, Ljava/lang/CharSequence;

    goto :goto_1e1

    .line 237
    :cond_252
    const-string v2, "ind"

    invoke-virtual {v2, v9}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v2

    if-eqz v2, :cond_25d

    const-string v2, "ind"

    goto :goto_221

    :cond_25d
    const-string v2, ""

    goto :goto_221

    :cond_260
    move v3, v6

    goto/16 :goto_a9
.end method

.method static tone(Landroid/content/Context;)Landroid/net/Uri;
    .registers 3

    .prologue
    .line 41
    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    const-string v1, "android.resource://"

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {p0}, Landroid/content/Context;->getPackageName()Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v1, "/"

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    const/high16 v1, 0x7f010000

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-static {v0}, Landroid/net/Uri;->parse(Ljava/lang/String;)Landroid/net/Uri;

    move-result-object v0

    return-object v0
.end method

.method static unpaired(Landroid/content/Context;)V
    .registers 5

    .prologue
    const/4 v3, 0x2

    .line 244
    invoke-static {p0}, Lcom/holy/dash/Notif;->nm(Landroid/content/Context;)Landroid/app/NotificationManager;

    move-result-object v0

    const-string v1, "alert2"

    invoke-static {p0, v1}, Lcom/holy/dash/Notif;->builder(Landroid/content/Context;Ljava/lang/String;)Landroid/app/Notification$Builder;

    move-result-object v1

    const-string v2, "\ud83d\udd17 \u0641\u064f\u0635\u0644 \u0647\u0630\u0627 \u0627\u0644\u0647\u0627\u062a\u0641 \u0639\u0646 \u0627\u0644\u0644\u0648\u062d\u0629"

    invoke-virtual {v1, v2}, Landroid/app/Notification$Builder;->setContentTitle(Ljava/lang/CharSequence;)Landroid/app/Notification$Builder;

    move-result-object v1

    const-string v2, "\u0627\u0641\u062a\u062d Holy \u0648\u0627\u062f\u062e\u0644 \u0627\u0644\u0644\u0648\u062d\u0629 \u0644\u062a\u0639\u0648\u062f \u0627\u0644\u0625\u0634\u0639\u0627\u0631\u0627\u062a"

    .line 245
    invoke-virtual {v1, v2}, Landroid/app/Notification$Builder;->setContentText(Ljava/lang/CharSequence;)Landroid/app/Notification$Builder;

    move-result-object v1

    const v2, -0x48e7b

    invoke-virtual {v1, v2}, Landroid/app/Notification$Builder;->setColor(I)Landroid/app/Notification$Builder;

    move-result-object v1

    const/4 v2, 0x1

    invoke-virtual {v1, v2}, Landroid/app/Notification$Builder;->setAutoCancel(Z)Landroid/app/Notification$Builder;

    move-result-object v1

    const-string v2, ""

    .line 246
    invoke-static {p0, v2, v3}, Lcom/holy/dash/Notif;->open(Landroid/content/Context;Ljava/lang/String;I)Landroid/app/PendingIntent;

    move-result-object v2

    invoke-virtual {v1, v2}, Landroid/app/Notification$Builder;->setContentIntent(Landroid/app/PendingIntent;)Landroid/app/Notification$Builder;

    move-result-object v1

    invoke-virtual {v1}, Landroid/app/Notification$Builder;->build()Landroid/app/Notification;

    move-result-object v1

    .line 244
    invoke-virtual {v0, v3, v1}, Landroid/app/NotificationManager;->notify(ILandroid/app/Notification;)V

    .line 247
    return-void
.end method

.method static watchHidden(Landroid/content/Context;)Z
    .registers 4

    .prologue
    const/4 v0, 0x0

    .line 115
    sget v1, Landroid/os/Build$VERSION;->SDK_INT:I

    const/16 v2, 0x1a

    if-ge v1, v2, :cond_8

    .line 120
    :cond_7
    :goto_7
    return v0

    .line 117
    :cond_8
    :try_start_8
    invoke-static {p0}, Lcom/holy/dash/Notif;->nm(Landroid/content/Context;)Landroid/app/NotificationManager;

    move-result-object v1

    const-string v2, "watch"

    invoke-virtual {v1, v2}, Landroid/app/NotificationManager;->getNotificationChannel(Ljava/lang/String;)Landroid/app/NotificationChannel;

    move-result-object v1

    .line 118
    if-eqz v1, :cond_7

    invoke-virtual {v1}, Landroid/app/NotificationChannel;->getImportance()I
    :try_end_17
    .catch Ljava/lang/Exception; {:try_start_8 .. :try_end_17} :catch_1c

    move-result v1

    if-nez v1, :cond_7

    const/4 v0, 0x1

    goto :goto_7

    .line 119
    :catch_1c
    move-exception v1

    goto :goto_7
.end method

.method static watching(Landroid/content/Context;Ljava/lang/String;)Landroid/app/Notification;
    .registers 5

    .prologue
    const/4 v2, 0x1

    .line 108
    const-string v0, "watch"

    invoke-static {p0, v0}, Lcom/holy/dash/Notif;->builder(Landroid/content/Context;Ljava/lang/String;)Landroid/app/Notification$Builder;

    move-result-object v0

    const-string v1, "Holy"

    invoke-virtual {v0, v1}, Landroid/app/Notification$Builder;->setContentTitle(Ljava/lang/CharSequence;)Landroid/app/Notification$Builder;

    move-result-object v0

    invoke-virtual {v0, p1}, Landroid/app/Notification$Builder;->setContentText(Ljava/lang/CharSequence;)Landroid/app/Notification$Builder;

    move-result-object v0

    invoke-virtual {v0, v2}, Landroid/app/Notification$Builder;->setOngoing(Z)Landroid/app/Notification$Builder;

    move-result-object v0

    const/4 v1, 0x0

    invoke-virtual {v0, v1}, Landroid/app/Notification$Builder;->setShowWhen(Z)Landroid/app/Notification$Builder;

    move-result-object v0

    const v1, -0xdd2c12

    .line 109
    invoke-virtual {v0, v1}, Landroid/app/Notification$Builder;->setColor(I)Landroid/app/Notification$Builder;

    move-result-object v0

    const-string v1, "service"

    invoke-virtual {v0, v1}, Landroid/app/Notification$Builder;->setCategory(Ljava/lang/String;)Landroid/app/Notification$Builder;

    move-result-object v0

    const/4 v1, -0x1

    invoke-virtual {v0, v1}, Landroid/app/Notification$Builder;->setVisibility(I)Landroid/app/Notification$Builder;

    move-result-object v0

    invoke-virtual {v0, v2}, Landroid/app/Notification$Builder;->setLocalOnly(Z)Landroid/app/Notification$Builder;

    move-result-object v0

    const/4 v1, 0x0

    .line 110
    invoke-static {p0, v1, v2}, Lcom/holy/dash/Notif;->open(Landroid/content/Context;Ljava/lang/String;I)Landroid/app/PendingIntent;

    move-result-object v1

    invoke-virtual {v0, v1}, Landroid/app/Notification$Builder;->setContentIntent(Landroid/app/PendingIntent;)Landroid/app/Notification$Builder;

    move-result-object v0

    invoke-virtual {v0}, Landroid/app/Notification$Builder;->build()Landroid/app/Notification;

    move-result-object v0

    .line 108
    return-object v0
.end method
