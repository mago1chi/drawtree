from django.shortcuts import render
from graphviz import Digraph
import re
import datetime

def index(request):
    sample_text = "主張\n  枠組み1\n    理由1\n    理由2\n    理由3\n  枠組み2\n    理由4\n    理由5\n    理由6\n  枠組み3\n    理由7\n    理由8\n"
    return render(request, 'drawlogic/colatest3.html', {'prev_text_body': sample_text, 'image_file_name': "drawlogic/sample.png"})

def draw(request):
    # セッションキーの取得
    if not request.session.session_key:
      request.session.create() 
    
    session_key = request.session.session_key

    prev_text_body = request.POST['text_logictree']
    text_body = prev_text_body.splitlines()
    
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
    
    # 有向グラフオブジェクトをインスタンス化
    graph_body = Digraph(format="png")
    graph_body.attr('node', shape='box', fontname='MS Gothic')

    parent_info_dict = {} #各階層レベルに対応する親ノード情報を保持する辞書
    parent_message = ""
    parent_depth = 0 #親ノードの階層レベルを記録する変数
    depth_diff = 0 #親ノードと直下の子ノードの深さを記録する変数
    graph_body.node(name=parsed_body_list[0]["message"], style='filled')
    
    # 各ノードごとにノード情報、リンク情報を抽出
    for index in range(1, len(parsed_body_list)):
        # 一つ深い階層に移動した際の処理
        if parsed_body_list[index]["depth"] - parent_depth > depth_diff:
            # 親ノード情報を更新
            parent_message = parsed_body_list[index-1]["message"]
            parent_depth = parsed_body_list[index-1]["depth"]
            
            # 現在の深さに対応する親ノード情報を記録（階層が浅い位置に戻った際に利用）
            parent_info_dict[parsed_body_list[index]["depth"]] = {
                    "parent_message": parent_message,
                    "parent_depth": parent_depth
                    }
            
            # 階層移動を検知するために親ノードと直下の子ノードの深さ差分を記録
            depth_diff = parsed_body_list[index]["depth"] - parent_depth
        
        # 階層が浅い位置に戻った際の処理
        elif parsed_body_list[index]["depth"] - parent_depth < depth_diff:
            try:
                # 現在の深さに対応する過去の親ノード情報からparent_message、parent_depthを更新
                parent_message = parent_info_dict[parsed_body_list[index]["depth"]]["parent_message"]
                parent_depth = parent_info_dict[parsed_body_list[index]["depth"]]["parent_depth"]
            except KeyError:
                return render(request, 'drawlogic/colatest3.html', {'err_message':"各階層のインデントを揃えてください。", 'prev_text_body': prev_text_body})
            
            # 階層移動を検知するために親ノードと直下の子ノードの深さ差分を記録
            depth_diff = parsed_body_list[index]["depth"] - parent_depth
        
        # 親ノードと現在のノードを結線
        graph_body.node(name=parsed_body_list[index]["message"], fontname="MS Gothic")
        graph_body.edge(parent_message, parsed_body_list[index]["message"])
        
    # 画像のレンダリング処理
    file_name = session_key+"_"+datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    graph_body.render(filename=file_name, directory="drawlogic/static/drawlogic/graph/")
    
    return render(request, 'drawlogic/colatest3.html', {'image_file_name':"drawlogic/graph/"+file_name+".png", 'prev_text_body': prev_text_body})

