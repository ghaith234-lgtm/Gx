.class Lcom/holy/dash/MainActivity$19;
.super Ljava/lang/Object;
.source "MainActivity.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/holy/dash/MainActivity;->bioDone(Ljava/lang/String;ILjava/lang/String;I)V
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
    .line 957
    iput-object p1, p0, Lcom/holy/dash/MainActivity$19;->this$0:Lcom/holy/dash/MainActivity;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .registers 3

    .prologue
    .line 957
    iget-object v0, p0, Lcom/holy/dash/MainActivity$19;->this$0:Lcom/holy/dash/MainActivity;

    iget-boolean v0, v0, Lcom/holy/dash/MainActivity;->bioBusy:Z

    if-eqz v0, :cond_10

    iget-object v0, p0, Lcom/holy/dash/MainActivity$19;->this$0:Lcom/holy/dash/MainActivity;

    const/4 v1, 0x0

    iput-boolean v1, v0, Lcom/holy/dash/MainActivity;->bioBusy:Z

    iget-object v0, p0, Lcom/holy/dash/MainActivity$19;->this$0:Lcom/holy/dash/MainActivity;

    invoke-virtual {v0}, Lcom/holy/dash/MainActivity;->hideLock()V

    :cond_10
    return-void
.end method
