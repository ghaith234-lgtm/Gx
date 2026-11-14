.class Lcom/holy/dash/Updater$3;
.super Ljava/lang/Object;
.source "Updater.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/holy/dash/Updater;->download(Landroid/app/Activity;Ljava/lang/String;Lorg/json/JSONObject;)V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic val$a:Landroid/app/Activity;

.field final synthetic val$apk:Lorg/json/JSONObject;

.field final synthetic val$origin:Ljava/lang/String;


# direct methods
.method constructor <init>(Landroid/app/Activity;Ljava/lang/String;Lorg/json/JSONObject;)V
    .registers 4
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .prologue
    .line 102
    iput-object p1, p0, Lcom/holy/dash/Updater$3;->val$a:Landroid/app/Activity;

    iput-object p2, p0, Lcom/holy/dash/Updater$3;->val$origin:Ljava/lang/String;

    iput-object p3, p0, Lcom/holy/dash/Updater$3;->val$apk:Lorg/json/JSONObject;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .registers 7

    .prologue
    const/4 v0, 0x0

    const/4 v5, 0x0

    .line 104
    .line 106
    :try_start_2
    new-instance v1, Ljava/io/File;

    iget-object v2, p0, Lcom/holy/dash/Updater$3;->val$a:Landroid/app/Activity;

    invoke-virtual {v2}, Landroid/app/Activity;->getCacheDir()Ljava/io/File;

    move-result-object v2

    const-string v3, "holy-update.apk"

    invoke-direct {v1, v2, v3}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    .line 107
    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    iget-object v3, p0, Lcom/holy/dash/Updater$3;->val$origin:Ljava/lang/String;

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    const-string v3, "/app/holy.apk"

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    iget-object v3, p0, Lcom/holy/dash/Updater$3;->val$a:Landroid/app/Activity;

    iget-object v4, p0, Lcom/holy/dash/Updater$3;->val$origin:Ljava/lang/String;

    invoke-static {v3, v4}, Lcom/holy/dash/Updater;->headers(Landroid/content/Context;Ljava/lang/String;)Ljava/util/Map;

    move-result-object v3

    const/4 v4, 0x0

    invoke-static {v2, v3, v1, v4}, Lcom/holy/dash/Net;->download(Ljava/lang/String;Ljava/util/Map;Ljava/io/File;Lcom/holy/dash/Net$Progress;)Ljava/lang/String;

    move-result-object v2

    .line 108
    iget-object v3, p0, Lcom/holy/dash/Updater$3;->val$apk:Lorg/json/JSONObject;

    const-string v4, "sha256"

    invoke-virtual {v3, v4}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v2, v3}, Ljava/lang/String;->equalsIgnoreCase(Ljava/lang/String;)Z

    move-result v2

    if-nez v2, :cond_59

    new-instance v0, Ljava/lang/SecurityException;

    const-string v1, "sha256"

    invoke-direct {v0, v1}, Ljava/lang/SecurityException;-><init>(Ljava/lang/String;)V

    throw v0
    :try_end_47
    .catch Ljava/lang/SecurityException; {:try_start_2 .. :try_end_47} :catch_47
    .catch Ljava/lang/Exception; {:try_start_2 .. :try_end_47} :catch_61
    .catchall {:try_start_2 .. :try_end_47} :catchall_67

    .line 110
    :catch_47
    move-exception v0

    .line 111
    :try_start_48
    const-string v0, "\u0648\u0635\u0644 \u0627\u0644\u0645\u0644\u0641 \u0646\u0627\u0642\u0635\u0627\u064b \u0623\u0648 \u0645\u062e\u062a\u0644\u0641\u0627\u064b \u2014 \u0644\u0646 \u064a\u064f\u062b\u0628\u064e\u0651\u062a"
    :try_end_4a
    .catchall {:try_start_48 .. :try_end_4a} :catchall_67

    .line 115
    sput-boolean v5, Lcom/holy/dash/Updater;->busy:Z

    .line 117
    :goto_4c
    if-eqz v0, :cond_58

    .line 119
    iget-object v1, p0, Lcom/holy/dash/Updater$3;->val$a:Landroid/app/Activity;

    new-instance v2, Lcom/holy/dash/Updater$3$1;

    invoke-direct {v2, p0, v0}, Lcom/holy/dash/Updater$3$1;-><init>(Lcom/holy/dash/Updater$3;Ljava/lang/String;)V

    invoke-virtual {v1, v2}, Landroid/app/Activity;->runOnUiThread(Ljava/lang/Runnable;)V

    .line 123
    :cond_58
    return-void

    .line 109
    :cond_59
    :try_start_59
    iget-object v2, p0, Lcom/holy/dash/Updater$3;->val$a:Landroid/app/Activity;

    invoke-static {v2, v1}, Lcom/holy/dash/Updater;->install(Landroid/content/Context;Ljava/io/File;)V
    :try_end_5e
    .catch Ljava/lang/SecurityException; {:try_start_59 .. :try_end_5e} :catch_47
    .catch Ljava/lang/Exception; {:try_start_59 .. :try_end_5e} :catch_61
    .catchall {:try_start_59 .. :try_end_5e} :catchall_67

    .line 115
    sput-boolean v5, Lcom/holy/dash/Updater;->busy:Z

    goto :goto_4c

    .line 112
    :catch_61
    move-exception v0

    .line 113
    :try_start_62
    const-string v0, "\u062a\u0639\u0630\u0651\u0631 \u062a\u0646\u0632\u064a\u0644 \u0627\u0644\u062a\u062d\u062f\u064a\u062b"
    :try_end_64
    .catchall {:try_start_62 .. :try_end_64} :catchall_67

    .line 115
    sput-boolean v5, Lcom/holy/dash/Updater;->busy:Z

    goto :goto_4c

    :catchall_67
    move-exception v0

    sput-boolean v5, Lcom/holy/dash/Updater;->busy:Z

    .line 116
    throw v0
.end method
