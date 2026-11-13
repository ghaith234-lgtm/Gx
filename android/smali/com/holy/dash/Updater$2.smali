.class Lcom/holy/dash/Updater$2;
.super Ljava/lang/Object;
.source "Updater.java"

# interfaces
.implements Landroid/content/DialogInterface$OnClickListener;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/holy/dash/Updater;->offer(Landroid/app/Activity;Ljava/lang/String;Lorg/json/JSONObject;)V
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
    .line 83
    iput-object p1, p0, Lcom/holy/dash/Updater$2;->val$a:Landroid/app/Activity;

    iput-object p2, p0, Lcom/holy/dash/Updater$2;->val$origin:Ljava/lang/String;

    iput-object p3, p0, Lcom/holy/dash/Updater$2;->val$apk:Lorg/json/JSONObject;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public onClick(Landroid/content/DialogInterface;I)V
    .registers 6

    .prologue
    .line 84
    iget-object v0, p0, Lcom/holy/dash/Updater$2;->val$a:Landroid/app/Activity;

    iget-object v1, p0, Lcom/holy/dash/Updater$2;->val$origin:Ljava/lang/String;

    iget-object v2, p0, Lcom/holy/dash/Updater$2;->val$apk:Lorg/json/JSONObject;

    invoke-static {v0, v1, v2}, Lcom/holy/dash/Updater;->download(Landroid/app/Activity;Ljava/lang/String;Lorg/json/JSONObject;)V

    return-void
.end method
