.class Lcom/holy/dash/MainActivity$14;
.super Ljava/lang/Object;
.source "MainActivity.java"

# interfaces
.implements Landroid/content/DialogInterface$OnClickListener;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/holy/dash/MainActivity;->askOem()V
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
    .line 690
    iput-object p1, p0, Lcom/holy/dash/MainActivity$14;->this$0:Lcom/holy/dash/MainActivity;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public onClick(Landroid/content/DialogInterface;I)V
    .registers 4

    .prologue
    .line 691
    iget-object v0, p0, Lcom/holy/dash/MainActivity$14;->this$0:Lcom/holy/dash/MainActivity;

    invoke-static {v0}, Lcom/holy/dash/Oem;->open(Landroid/app/Activity;)Ljava/lang/String;

    return-void
.end method
