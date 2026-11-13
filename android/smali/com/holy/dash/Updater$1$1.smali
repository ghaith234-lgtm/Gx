.class Lcom/holy/dash/Updater$1$1;
.super Ljava/lang/Object;
.source "Updater.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/holy/dash/Updater$1;->run()V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic this$0:Lcom/holy/dash/Updater$1;

.field final synthetic val$apk:Lorg/json/JSONObject;

.field final synthetic val$code:I


# direct methods
.method constructor <init>(Lcom/holy/dash/Updater$1;ILorg/json/JSONObject;)V
    .registers 4
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .prologue
    .line 62
    iput-object p1, p0, Lcom/holy/dash/Updater$1$1;->this$0:Lcom/holy/dash/Updater$1;

    iput p2, p0, Lcom/holy/dash/Updater$1$1;->val$code:I

    iput-object p3, p0, Lcom/holy/dash/Updater$1$1;->val$apk:Lorg/json/JSONObject;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .registers 5

    .prologue
    const-wide/16 v2, 0x0

    .line 64
    iget-object v0, p0, Lcom/holy/dash/Updater$1$1;->this$0:Lcom/holy/dash/Updater$1;

    iget-object v0, v0, Lcom/holy/dash/Updater$1;->val$a:Landroid/app/Activity;

    invoke-virtual {v0}, Landroid/app/Activity;->isFinishing()Z

    move-result v0

    if-eqz v0, :cond_d

    .line 67
    :cond_c
    :goto_c
    return-void

    .line 65
    :cond_d
    iget v0, p0, Lcom/holy/dash/Updater$1$1;->val$code:I

    const/16 v1, 0xb

    if-le v0, v1, :cond_2d

    iget-object v0, p0, Lcom/holy/dash/Updater$1$1;->val$apk:Lorg/json/JSONObject;

    const-string v1, "size"

    invoke-virtual {v0, v1, v2, v3}, Lorg/json/JSONObject;->optLong(Ljava/lang/String;J)J

    move-result-wide v0

    cmp-long v0, v0, v2

    if-lez v0, :cond_2d

    iget-object v0, p0, Lcom/holy/dash/Updater$1$1;->this$0:Lcom/holy/dash/Updater$1;

    iget-object v0, v0, Lcom/holy/dash/Updater$1;->val$a:Landroid/app/Activity;

    iget-object v1, p0, Lcom/holy/dash/Updater$1$1;->this$0:Lcom/holy/dash/Updater$1;

    iget-object v1, v1, Lcom/holy/dash/Updater$1;->val$origin:Ljava/lang/String;

    iget-object v2, p0, Lcom/holy/dash/Updater$1$1;->val$apk:Lorg/json/JSONObject;

    invoke-static {v0, v1, v2}, Lcom/holy/dash/Updater;->offer(Landroid/app/Activity;Ljava/lang/String;Lorg/json/JSONObject;)V

    goto :goto_c

    .line 66
    :cond_2d
    iget-object v0, p0, Lcom/holy/dash/Updater$1$1;->this$0:Lcom/holy/dash/Updater$1;

    iget-boolean v0, v0, Lcom/holy/dash/Updater$1;->val$manual:Z

    if-eqz v0, :cond_c

    iget-object v0, p0, Lcom/holy/dash/Updater$1$1;->this$0:Lcom/holy/dash/Updater$1;

    iget-object v0, v0, Lcom/holy/dash/Updater$1;->val$a:Landroid/app/Activity;

    const-string v1, "\u2705 \u0639\u0646\u062f\u0643 \u0622\u062e\u0631 \u0646\u0633\u062e\u0629 (2.0)"

    const/4 v2, 0x0

    invoke-static {v0, v1, v2}, Landroid/widget/Toast;->makeText(Landroid/content/Context;Ljava/lang/CharSequence;I)Landroid/widget/Toast;

    move-result-object v0

    invoke-virtual {v0}, Landroid/widget/Toast;->show()V

    goto :goto_c
.end method
