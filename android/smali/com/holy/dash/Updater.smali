.class final Lcom/holy/dash/Updater;
.super Ljava/lang/Object;
.source "Updater.java"


# static fields
.field static volatile busy:Z

.field static volatile lastAuto:J


# direct methods
.method private constructor <init>()V
    .registers 1

    .prologue
    .line 31
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method static check(Landroid/app/Activity;Z)V
    .registers 6

    .prologue
    .line 50
    sget-boolean v0, Lcom/holy/dash/Updater;->busy:Z

    if-eqz v0, :cond_5

    .line 76
    :cond_4
    :goto_4
    return-void

    .line 51
    :cond_5
    if-nez p1, :cond_15

    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v0

    sget-wide v2, Lcom/holy/dash/Updater;->lastAuto:J

    sub-long/2addr v0, v2

    const-wide/32 v2, 0x1499700

    cmp-long v0, v0, v2

    if-ltz v0, :cond_4

    .line 52
    :cond_15
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v0

    sput-wide v0, Lcom/holy/dash/Updater;->lastAuto:J

    .line 53
    invoke-static {p0}, Lcom/holy/dash/Prefs;->origin(Landroid/content/Context;)Ljava/lang/String;

    move-result-object v0

    .line 54
    invoke-virtual {v0}, Ljava/lang/String;->isEmpty()Z

    move-result v1

    if-nez v1, :cond_4

    .line 55
    new-instance v1, Ljava/lang/Thread;

    new-instance v2, Lcom/holy/dash/Updater$1;

    invoke-direct {v2, v0, p0, p1}, Lcom/holy/dash/Updater$1;-><init>(Ljava/lang/String;Landroid/app/Activity;Z)V

    const-string v0, "holy-update-check"

    invoke-direct {v1, v2, v0}, Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;Ljava/lang/String;)V

    .line 75
    invoke-virtual {v1}, Ljava/lang/Thread;->start()V

    goto :goto_4
.end method

.method static download(Landroid/app/Activity;Ljava/lang/String;Lorg/json/JSONObject;)V
    .registers 7

    .prologue
    const/4 v2, 0x1

    .line 91
    sget v0, Landroid/os/Build$VERSION;->SDK_INT:I

    const/16 v1, 0x1a

    if-lt v0, v1, :cond_40

    invoke-virtual {p0}, Landroid/app/Activity;->getPackageManager()Landroid/content/pm/PackageManager;

    move-result-object v0

    invoke-virtual {v0}, Landroid/content/pm/PackageManager;->canRequestPackageInstalls()Z

    move-result v0

    if-nez v0, :cond_40

    .line 92
    const-string v0, "\u0627\u0633\u0645\u062d \u0644\u0640 Holy \u064a\u062b\u0628\u0651\u062a \u062a\u062d\u062f\u064a\u062b\u0627\u062a\u0647\u060c \u0648\u0627\u0631\u062c\u0639 \u0627\u0636\u063a\u0637 \u062a\u062d\u062f\u064a\u062b"

    invoke-static {p0, v0, v2}, Landroid/widget/Toast;->makeText(Landroid/content/Context;Ljava/lang/CharSequence;I)Landroid/widget/Toast;

    move-result-object v0

    invoke-virtual {v0}, Landroid/widget/Toast;->show()V

    .line 94
    :try_start_1a
    new-instance v0, Landroid/content/Intent;

    const-string v1, "android.settings.MANAGE_UNKNOWN_APP_SOURCES"

    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    const-string v3, "package:"

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {p0}, Landroid/app/Activity;->getPackageName()Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    invoke-static {v2}, Landroid/net/Uri;->parse(Ljava/lang/String;)Landroid/net/Uri;

    move-result-object v2

    invoke-direct {v0, v1, v2}, Landroid/content/Intent;-><init>(Ljava/lang/String;Landroid/net/Uri;)V

    invoke-virtual {p0, v0}, Landroid/app/Activity;->startActivity(Landroid/content/Intent;)V
    :try_end_3f
    .catch Ljava/lang/Exception; {:try_start_1a .. :try_end_3f} :catch_5c

    .line 125
    :goto_3f
    return-void

    .line 100
    :cond_40
    sput-boolean v2, Lcom/holy/dash/Updater;->busy:Z

    .line 101
    const-string v0, "\u23f3 \u064a\u0646\u0632\u0644 \u0627\u0644\u062a\u062d\u062f\u064a\u062b\u2026"

    const/4 v1, 0x0

    invoke-static {p0, v0, v1}, Landroid/widget/Toast;->makeText(Landroid/content/Context;Ljava/lang/CharSequence;I)Landroid/widget/Toast;

    move-result-object v0

    invoke-virtual {v0}, Landroid/widget/Toast;->show()V

    .line 102
    new-instance v0, Ljava/lang/Thread;

    new-instance v1, Lcom/holy/dash/Updater$3;

    invoke-direct {v1, p0, p1, p2}, Lcom/holy/dash/Updater$3;-><init>(Landroid/app/Activity;Ljava/lang/String;Lorg/json/JSONObject;)V

    const-string v2, "holy-update"

    invoke-direct {v0, v1, v2}, Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;Ljava/lang/String;)V

    .line 124
    invoke-virtual {v0}, Ljava/lang/Thread;->start()V

    goto :goto_3f

    .line 95
    :catch_5c
    move-exception v0

    goto :goto_3f
.end method

.method static headers(Landroid/content/Context;Ljava/lang/String;)Ljava/util/Map;
    .registers 5
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Landroid/content/Context;",
            "Ljava/lang/String;",
            ")",
            "Ljava/util/Map",
            "<",
            "Ljava/lang/String;",
            "Ljava/lang/String;",
            ">;"
        }
    .end annotation

    .prologue
    .line 37
    new-instance v0, Ljava/util/HashMap;

    invoke-direct {v0}, Ljava/util/HashMap;-><init>()V

    .line 38
    invoke-static {p0}, Lcom/holy/dash/Prefs;->token(Landroid/content/Context;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/String;->isEmpty()Z

    move-result v1

    if-nez v1, :cond_18

    const-string v1, "X-Holy-Device"

    invoke-static {p0}, Lcom/holy/dash/Prefs;->token(Landroid/content/Context;)Ljava/lang/String;

    move-result-object v2

    invoke-interface {v0, v1, v2}, Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;

    .line 40
    :cond_18
    :try_start_18
    invoke-static {}, Landroid/webkit/CookieManager;->getInstance()Landroid/webkit/CookieManager;

    move-result-object v1

    invoke-virtual {v1, p1}, Landroid/webkit/CookieManager;->getCookie(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    .line 41
    if-eqz v1, :cond_27

    const-string v2, "Cookie"

    invoke-interface {v0, v2, v1}, Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_27
    .catch Ljava/lang/Exception; {:try_start_18 .. :try_end_27} :catch_28

    .line 45
    :cond_27
    :goto_27
    return-object v0

    .line 42
    :catch_28
    move-exception v1

    goto :goto_27
.end method

.method static install(Landroid/content/Context;Ljava/io/File;)V
    .registers 11
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/lang/Exception;
        }
    .end annotation

    .prologue
    const/16 v8, 0x1f

    const/4 v6, 0x0

    .line 128
    invoke-virtual {p0}, Landroid/content/Context;->getPackageManager()Landroid/content/pm/PackageManager;

    move-result-object v0

    invoke-virtual {v0}, Landroid/content/pm/PackageManager;->getPackageInstaller()Landroid/content/pm/PackageInstaller;

    move-result-object v0

    .line 129
    new-instance v1, Landroid/content/pm/PackageInstaller$SessionParams;

    const/4 v2, 0x1

    invoke-direct {v1, v2}, Landroid/content/pm/PackageInstaller$SessionParams;-><init>(I)V

    .line 130
    invoke-virtual {p0}, Landroid/content/Context;->getPackageName()Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v1, v2}, Landroid/content/pm/PackageInstaller$SessionParams;->setAppPackageName(Ljava/lang/String;)V

    .line 131
    sget v2, Landroid/os/Build$VERSION;->SDK_INT:I

    if-lt v2, v8, :cond_20

    const/4 v2, 0x2

    invoke-virtual {v1, v2}, Landroid/content/pm/PackageInstaller$SessionParams;->setRequireUserAction(I)V

    .line 132
    :cond_20
    invoke-virtual {v0, v1}, Landroid/content/pm/PackageInstaller;->createSession(Landroid/content/pm/PackageInstaller$SessionParams;)I

    move-result v7

    .line 133
    invoke-virtual {v0, v7}, Landroid/content/pm/PackageInstaller;->openSession(I)Landroid/content/pm/PackageInstaller$Session;

    move-result-object v0

    .line 135
    :try_start_28
    const-string v1, "holy.apk"

    const-wide/16 v2, 0x0

    invoke-virtual {p1}, Ljava/io/File;->length()J

    move-result-wide v4

    invoke-virtual/range {v0 .. v5}, Landroid/content/pm/PackageInstaller$Session;->openWrite(Ljava/lang/String;JJ)Ljava/io/OutputStream;

    move-result-object v2

    .line 136
    new-instance v3, Ljava/io/FileInputStream;

    invoke-direct {v3, p1}, Ljava/io/FileInputStream;-><init>(Ljava/io/File;)V
    :try_end_39
    .catchall {:try_start_28 .. :try_end_39} :catchall_50

    .line 138
    const/high16 v1, 0x10000

    :try_start_3b
    new-array v1, v1, [B

    .line 140
    :goto_3d
    invoke-virtual {v3, v1}, Ljava/io/InputStream;->read([B)I

    move-result v4

    if-lez v4, :cond_55

    const/4 v5, 0x0

    invoke-virtual {v2, v1, v5, v4}, Ljava/io/OutputStream;->write([BII)V
    :try_end_47
    .catchall {:try_start_3b .. :try_end_47} :catchall_48

    goto :goto_3d

    .line 143
    :catchall_48
    move-exception v1

    :try_start_49
    invoke-virtual {v3}, Ljava/io/InputStream;->close()V

    .line 144
    invoke-virtual {v2}, Ljava/io/OutputStream;->close()V

    .line 145
    throw v1
    :try_end_50
    .catchall {:try_start_49 .. :try_end_50} :catchall_50

    .line 150
    :catchall_50
    move-exception v1

    invoke-virtual {v0}, Landroid/content/pm/PackageInstaller$Session;->close()V

    .line 151
    throw v1

    .line 141
    :cond_55
    :try_start_55
    invoke-virtual {v0, v2}, Landroid/content/pm/PackageInstaller$Session;->fsync(Ljava/io/OutputStream;)V
    :try_end_58
    .catchall {:try_start_55 .. :try_end_58} :catchall_48

    .line 143
    :try_start_58
    invoke-virtual {v3}, Ljava/io/InputStream;->close()V

    .line 144
    invoke-virtual {v2}, Ljava/io/OutputStream;->close()V

    .line 146
    new-instance v2, Landroid/content/Intent;

    const-class v1, Lcom/holy/dash/InstallReceiver;

    invoke-direct {v2, p0, v1}, Landroid/content/Intent;-><init>(Landroid/content/Context;Ljava/lang/Class;)V

    .line 147
    const/high16 v3, 0x8000000

    sget v1, Landroid/os/Build$VERSION;->SDK_INT:I

    if-lt v1, v8, :cond_7d

    const/high16 v1, 0x2000000

    :goto_6d
    or-int/2addr v1, v3

    .line 148
    invoke-static {p0, v7, v2, v1}, Landroid/app/PendingIntent;->getBroadcast(Landroid/content/Context;ILandroid/content/Intent;I)Landroid/app/PendingIntent;

    move-result-object v1

    invoke-virtual {v1}, Landroid/app/PendingIntent;->getIntentSender()Landroid/content/IntentSender;

    move-result-object v1

    invoke-virtual {v0, v1}, Landroid/content/pm/PackageInstaller$Session;->commit(Landroid/content/IntentSender;)V
    :try_end_79
    .catchall {:try_start_58 .. :try_end_79} :catchall_50

    .line 150
    invoke-virtual {v0}, Landroid/content/pm/PackageInstaller$Session;->close()V

    .line 152
    return-void

    :cond_7d
    move v1, v6

    .line 147
    goto :goto_6d
.end method

.method static offer(Landroid/app/Activity;Ljava/lang/String;Lorg/json/JSONObject;)V
    .registers 11

    .prologue
    .line 79
    sget-object v0, Ljava/util/Locale;->US:Ljava/util/Locale;

    const-string v1, "%.0f KB"

    const/4 v2, 0x1

    new-array v2, v2, [Ljava/lang/Object;

    const/4 v3, 0x0

    const-string v4, "size"

    const-wide/16 v6, 0x0

    invoke-virtual {p2, v4, v6, v7}, Lorg/json/JSONObject;->optLong(Ljava/lang/String;J)J

    move-result-wide v4

    long-to-double v4, v4

    const-wide/high16 v6, 0x4090000000000000L    # 1024.0

    div-double/2addr v4, v6

    invoke-static {v4, v5}, Ljava/lang/Double;->valueOf(D)Ljava/lang/Double;

    move-result-object v4

    aput-object v4, v2, v3

    invoke-static {v0, v1, v2}, Ljava/lang/String;->format(Ljava/util/Locale;Ljava/lang/String;[Ljava/lang/Object;)Ljava/lang/String;

    move-result-object v0

    .line 80
    new-instance v1, Landroid/app/AlertDialog$Builder;

    const v2, 0x10302d1

    invoke-direct {v1, p0, v2}, Landroid/app/AlertDialog$Builder;-><init>(Landroid/content/Context;I)V

    const-string v2, "\u2b06\ufe0f \u062a\u062d\u062f\u064a\u062b \u0644\u0644\u062a\u0637\u0628\u064a\u0642"

    .line 81
    invoke-virtual {v1, v2}, Landroid/app/AlertDialog$Builder;->setTitle(Ljava/lang/CharSequence;)Landroid/app/AlertDialog$Builder;

    move-result-object v1

    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    const-string v3, "\u0646\u0633\u062e\u0629 \u062c\u062f\u064a\u062f\u0629 \u0645\u0646 Holy: "

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    const-string v3, "name"

    .line 82
    invoke-virtual {p2, v3}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    const-string v3, " ("

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v2, ")\n\u0639\u0646\u062f\u0643: "

    invoke-virtual {v0, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v2, "2.0"

    invoke-virtual {v0, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v2, "\n\n\u064a\u062a\u062d\u062f\u062b \u0627\u0644\u062d\u064a\u0646\u061f"

    invoke-virtual {v0, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-virtual {v1, v0}, Landroid/app/AlertDialog$Builder;->setMessage(Ljava/lang/CharSequence;)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    const-string v1, "\u062a\u062d\u062f\u064a\u062b"

    new-instance v2, Lcom/holy/dash/Updater$2;

    invoke-direct {v2, p0, p1, p2}, Lcom/holy/dash/Updater$2;-><init>(Landroid/app/Activity;Ljava/lang/String;Lorg/json/JSONObject;)V

    .line 83
    invoke-virtual {v0, v1, v2}, Landroid/app/AlertDialog$Builder;->setPositiveButton(Ljava/lang/CharSequence;Landroid/content/DialogInterface$OnClickListener;)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    const-string v1, "\u0628\u0639\u062f\u064a\u0646"

    const/4 v2, 0x0

    .line 86
    invoke-virtual {v0, v1, v2}, Landroid/app/AlertDialog$Builder;->setNegativeButton(Ljava/lang/CharSequence;Landroid/content/DialogInterface$OnClickListener;)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    .line 87
    invoke-virtual {v0}, Landroid/app/AlertDialog$Builder;->show()Landroid/app/AlertDialog;

    .line 88
    return-void
.end method
