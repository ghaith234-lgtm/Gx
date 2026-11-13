.class Lcom/holy/dash/MainActivity$5;
.super Ljava/lang/Object;
.source "MainActivity.java"

# interfaces
.implements Landroid/widget/TextView$OnEditorActionListener;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/holy/dash/MainActivity;->showSetup(Ljava/lang/String;)V
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
    .line 282
    iput-object p1, p0, Lcom/holy/dash/MainActivity$5;->this$0:Lcom/holy/dash/MainActivity;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public onEditorAction(Landroid/widget/TextView;ILandroid/view/KeyEvent;)Z
    .registers 6

    .prologue
    .line 283
    iget-object v0, p0, Lcom/holy/dash/MainActivity$5;->this$0:Lcom/holy/dash/MainActivity;

    const/4 v1, 0x0

    invoke-virtual {v0, v1}, Lcom/holy/dash/MainActivity;->connect(Z)V

    const/4 v0, 0x1

    return v0
.end method
