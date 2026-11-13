.class Lcom/holy/dash/MainActivity$12;
.super Ljava/lang/Object;
.source "MainActivity.java"

# interfaces
.implements Landroid/webkit/ValueCallback;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/holy/dash/MainActivity;->runGo()V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation

.annotation system Ldalvik/annotation/Signature;
    value = {
        "Ljava/lang/Object;",
        "Landroid/webkit/ValueCallback",
        "<",
        "Ljava/lang/String;",
        ">;"
    }
.end annotation


# instance fields
.field final synthetic this$0:Lcom/holy/dash/MainActivity;

.field final synthetic val$g:Ljava/lang/String;


# direct methods
.method constructor <init>(Lcom/holy/dash/MainActivity;Ljava/lang/String;)V
    .registers 3
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .prologue
    .line 642
    iput-object p1, p0, Lcom/holy/dash/MainActivity$12;->this$0:Lcom/holy/dash/MainActivity;

    iput-object p2, p0, Lcom/holy/dash/MainActivity$12;->val$g:Ljava/lang/String;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public bridge synthetic onReceiveValue(Ljava/lang/Object;)V
    .registers 2

    .prologue
    .line 642
    check-cast p1, Ljava/lang/String;

    invoke-virtual {p0, p1}, Lcom/holy/dash/MainActivity$12;->onReceiveValue(Ljava/lang/String;)V

    return-void
.end method

.method public onReceiveValue(Ljava/lang/String;)V
    .registers 4

    .prologue
    .line 644
    const-string v0, "\"1\""

    invoke-virtual {v0, p1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-nez v0, :cond_14

    iget-object v0, p0, Lcom/holy/dash/MainActivity$12;->this$0:Lcom/holy/dash/MainActivity;

    iget-object v0, v0, Lcom/holy/dash/MainActivity;->pendingGo:Ljava/lang/String;

    if-nez v0, :cond_14

    iget-object v0, p0, Lcom/holy/dash/MainActivity$12;->this$0:Lcom/holy/dash/MainActivity;

    iget-object v1, p0, Lcom/holy/dash/MainActivity$12;->val$g:Ljava/lang/String;

    iput-object v1, v0, Lcom/holy/dash/MainActivity;->pendingGo:Ljava/lang/String;

    .line 645
    :cond_14
    return-void
.end method
