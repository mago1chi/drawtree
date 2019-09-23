from django.shortcuts import render
import re
import json

# Create your views here.

def index(request):
    return render(request, 'drawlogic/colatest3.html', {'path_to_json': 'drawlogic/cities.json'})

def draw(request):
    text_body = request.POST['text_logictree'].splitlines()
    
    # 入力されたメッセージを一行ごとに正規表現でパースし、
    # 各行のID、階層レベル、メッセージを辞書型で抽出＆リスト化
    parsed_body_list = []
    for index in range(len(text_body)):
        parsed_body = re.search(r"^(\s*)(.*)", text_body[index])
        tmp_dict = {
                "id": index,
                "depth": len(parsed_body.group(1)) if parsed_body.group(1) is not None else 0,
                "message": parsed_body.group(2)
                }
        parsed_body_list.append(tmp_dict)
    
    node_list = [{
        "name": parsed_body_list[0]["message"],
        "width": 200,
        "height": 40
        }] #各ノードのメッセージを保持するリスト（rootノード情報のみ初期状態で格納）
    link_list = [] #ノード間のリンク情報を保持するリスト
    parent_info_dict = {} #各階層レベルに対応する親ノード情報を保持する辞書
    parent_id = 0 #親ノードのIDを記録する変数
    parent_depth = 0 #親ノードの階層レベルを記録する変数
    depth_diff = 0 #親ノードと直下の子ノードの深さを記録する変数
    
    # 各ノードごとにノード情報、リンク情報を抽出
    for index in range(1, len(parsed_body_list)):
        # 当該ノードのノード情報を記録
        node_list.append({
            "name": parsed_body_list[index]["message"],
            "width": 200,
            "height": 40
            })
        
        # 一つ深い階層に移動した際の処理
        if parsed_body_list[index]["depth"] - parent_depth > depth_diff:
            # 親ノード情報を更新
            parent_id = parsed_body_list[index-1]["id"]
            parent_depth = parsed_body_list[index-1]["depth"]
            
            # 現在の深さに対応する親ノード情報を記録（階層が浅い位置に戻った際に利用）
            parent_info_dict[parsed_body_list[index]["depth"]] = {
                    "parent_id": parent_id,
                    "parent_depth": parent_depth
                    }
            
            # 階層移動を検知するために親ノードと直下の子ノードの深さ差分を記録
            depth_diff = parsed_body_list[index]["depth"] - parent_depth
        
        # 階層が浅い位置に戻った際の処理
        elif parsed_body_list[index]["depth"] - parent_depth < depth_diff:
            # 現在の深さに対応する過去の親ノード情報からparent_id、parent_depthを更新
            parent_id = parent_info_dict[parsed_body_list[index]["depth"]]["parent_id"]
            parent_depth = parent_info_dict[parsed_body_list[index]["depth"]]["parent_depth"]
            
            # 階層移動を検知するために親ノードと直下の子ノードの深さ差分を記録
            depth_diff = parsed_body_list[index]["depth"] - parent_depth
        
        # 当該ノードのリンク情報を記録
        link_list.append({
                "source": parsed_body_list[index]["id"],
                "target": parent_id,
                })
        
    # cold.jsに読み込ませるグラフ情報をまとめる
    json_body = {"nodes": node_list, "links": link_list}
    
    # グラフ情報をjsonファイルとして書き出し、cola.jsが読み込めるようにする
    with open('C:/Users/shoul/OneDrive/ドキュメント/ものづくり/ロジックツリー作成ツール/logictree/drawlogic/static/drawlogic/tmp.json', 'w') as f:
        f.write(json.dumps(json_body))
    
    return render(request, 'drawlogic/colatest3.html', {'path_to_json': 'drawlogic/tmp.json'})

