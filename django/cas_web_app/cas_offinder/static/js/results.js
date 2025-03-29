function one_mismatch_rank_table(id, name, _class, _rank_data_list, show_max){
    document.write(`<table id=${id} name=${name}>`);
    document.getElementById(id).className=_class;

    var column_info_list = [
        {"class" : "MMTableRank",    "name" : "Rank"         , "row" : 2, "col" : 1},
        {"class" : "MMTableSeq",     "name" : "Sequence"     , "row" : 2, "col" : 1},
        {"class" : "MMTableMM",      "name" : "Mismatch"     , "row" : 2, "col" : 1},
        {"class" : "MMTableMMInfo",  "name" : "Mispaired info", "row" : 2, "col" : 1},
        {"class" : "MMTableScore",   "name" : "NCS"        , "row" : 1, "col" : 1},
        {"class" : "MMTableMMs",     "name" : "Summation of mismatches"   , "row" : 1, "col" : 5},
    ];
    var mismatch_column_list = [
        {"class" : "MMTableScore2", "name" : "(higher is better)" , "row" : 1, "col" : 1},
        {"class" : "MMTableMMEach",    "name" : "0" , "row" : 1, "col" : 1},
        {"class" : "MMTableMMEach",    "name" : "1" , "row" : 1, "col" : 1},
        {"class" : "MMTableMMEach",    "name" : "2" , "row" : 1, "col" : 1},
        {"class" : "MMTableMMEach",    "name" : "3" , "row" : 1, "col" : 1},
        {"class" : "MMTableMMEach",    "name" : "4" , "row" : 1, "col" : 1},
        //{"name" : "5" , "row" : 1, "col" : 1},
    ];
    var rank_data_list = _rank_data_list.slice(undefined,show_max+1);
    
    //column - Rank Sequence Score Mismatches
    document.write("<thead>")
    document.write("<tr>");
    for (var i=0; i < column_info_list.length; i++){
        var info = column_info_list[i];
        document.write(`<th class=${info.class} rowspan=${info.row} colspan=${info.col}>${info.name}</th>`);
    }
    document.write("</tr>");

    //column - mismatch 0 1 2 3 4 5
    document.write("<tr>");
    for (var i=0; i < mismatch_column_list.length; i++){
        var info = mismatch_column_list[i];
        document.write(`<th class=${info.class} rowspan=${info.row} colspan=${info.col}>${info.name}</th>`);
    }
    document.write("</tr>");
    document.write("</thead>")

    //rank_data
    for (var i=0; i < rank_data_list.length; i++){
        var info = rank_data_list[i];
        var rank_num = i
        if (rank_num == 0){
            rank_num = "Query";
            document.write("<tr style='background: #d2d2d2;'>");
            document.write(`<td>${rank_num}</td>`);
            document.write(`<td>${info.target}</td>`);
            document.write(`<td>${info.num_mm}</td>`);
            document.write(`<td>${info.mm_info}</td>`);
            document.write(`<td>${info.score.toFixed(4)}</td>`);
            //document.write(`<td>${info.score}</td>`);
            document.write(`<td>${info.mismatch_0}</td>`);
            document.write(`<td>${info.mismatch_1}</td>`);
            document.write(`<td>${info.mismatch_2}</td>`);
            document.write(`<td>${info.mismatch_3}</td>`);
            document.write(`<td>${info.mismatch_4}</td>`);
            //for (var j=0; j < 5;j++){
            //    document.write(`<td>${info.mismatch_count[j]}</td>`)
            //}
            document.write("</tr>");
            continue;
        }
        document.write("<tr>");
        document.write(`<td>${rank_num}</td>`);
        document.write(`<td><a href="${rank_num}" target="_blank" rel="noopener noreferrer">${info.target}</a></td>`);
        document.write(`<td>${info.num_mm}</td>`);
        document.write(`<td>${info.mm_info}</td>`);
        document.write(`<td>${info.score.toFixed(4)}</td>`);
        document.write(`<td>${info.mismatch_0}</td>`);
        document.write(`<td>${info.mismatch_1}</td>`);
        document.write(`<td>${info.mismatch_2}</td>`);
        document.write(`<td>${info.mismatch_3}</td>`);
        document.write(`<td>${info.mismatch_4}</td>`);
        //for (var j=0; j < 5;j++){
        //    document.write(`<td>${info.mismatch_count[j]}</td>`)
        //}
        document.write("</tr>");
    }
    document.write(`</table>`);


}
