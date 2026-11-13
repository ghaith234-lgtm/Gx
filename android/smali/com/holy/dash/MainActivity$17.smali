.class Lcom/holy/dash/MainActivity$17;
.super Ljava/lang/Object;
.source "MainActivity.java"

# interfaces
.implements Lcom/holy/dash/Bio$Done;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/holy/dash/MainActivity;->askAuth()V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic this$0:Lcom/holy/dash/MainActivity;


# direct methods
.method constructor <init>(Lcom/holy/dash/MainActivity;)V
    .registers 2

    .prologue
    .line 863
    iput-object p1, p0, Lcom/holy/dash/MainActivity$17;->this$0:Lcom/holy/dash/MainActivity;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public cancelled()V
    .registers 3

    .prologue
    .line 866
    iget-object v0, p0, Lcom/holy/dash/MainActivity$17;->this$0:Lcom/holy/dash/MainActivity;

    const/4 v1, 0x0

    iput-boolean v1, v0, Lcom/holy/dash/MainActivity;->authBusy:Z

    iget-object v0, p0, Lcom/holy/dash/MainActivity$17;->this$0:Lcom/holy/dash/MainActivity;

    const/4 v1, 0x0

    invoke-virtual {v0, v1}, Lcom/holy/dash/MainActivity;->authFail(Ljava/lang/String;)V

    return-void
.end method

.method public fallback()V
    .registers 3

    .prologue
    .line 868
    iget-object v0, p0, Lcom/holy/dash/MainActivity$17;->this$0:Lcom/holy/dash/MainActivity;

    const/4 v1, 0x0

    iput-boolean v1, v0, Lcom/holy/dash/MainActivity;->authBusy:Z

    iget-object v0, p0, Lcom/holy/dash/MainActivity$17;->this$0:Lcom/holy/dash/MainActivity;

    invoke-virtual {v0}, Lcom/holy/dash/MainActivity;->keyguard()V

    return-void
.end method

.method public ok()V
    .registers 3

    .prologue
    .line 864
    iget-object v0, p0, Lcom/holy/dash/MainActivity$17;->this$0:Lcom/holy/dash/MainActivity;

    const/4 v1, 0x0

    iput-boolean v1, v0, Lcom/holy/dash/MainActivity;->authBusy:Z

    iget-object v0, p0, Lcom/holy/dash/MainActivity$17;->this$0:Lcom/holy/dash/MainActivity;

    invoke-virtual {v0}, Lcom/holy/dash/MainActivity;->authOk()V

    return-void
.end method
