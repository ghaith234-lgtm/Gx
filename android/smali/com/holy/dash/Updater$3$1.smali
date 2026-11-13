.class Lcom/holy/dash/Updater$3$1;
.super Ljava/lang/Object;
.source "Updater.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/holy/dash/Updater$3;->run()V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic this$0:Lcom/holy/dash/Updater$3;

.field final synthetic val$m:Ljava/lang/String;


# direct methods
.method constructor <init>(Lcom/holy/dash/Updater$3;Ljava/lang/String;)V
    .registers 3
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .prologue
    .line 119
    iput-object p1, p0, Lcom/holy/dash/Updater$3$1;->this$0:Lcom/holy/dash/Updater$3;

    iput-object p2, p0, Lcom/holy/dash/Updater$3$1;->val$m:Ljava/lang/String;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .registers 4

    .prologue
    .line 120
    iget-object v0, p0, Lcom/holy/dash/Updater$3$1;->this$0:Lcom/holy/dash/Updater$3;

    iget-object v0, v0, Lcom/holy/dash/Updater$3;->val$a:Landroid/app/Activity;

    iget-object v1, p0, Lcom/holy/dash/Updater$3$1;->val$m:Ljava/lang/String;

    const/4 v2, 0x1

    invoke-static {v0, v1, v2}, Landroid/widget/Toast;->makeText(Landroid/content/Context;Ljava/lang/CharSequence;I)Landroid/widget/Toast;

    move-result-object v0

    invoke-virtual {v0}, Landroid/widget/Toast;->show()V

    return-void
.end method
