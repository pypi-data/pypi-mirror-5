var playarea = new Array(64);

var currentColor = null;
var debug = false;

var KING = 'King';
var QUEEN = 'Queen';
var ROOK = 'Rook';
var KNIGHT = 'Knight';
var BISHOP = 'Bishop';
var PAWN = 'Pawn';

var BLACK = 0;
var WHITE = 1;
var OPEN = 2;
var X = 0;
var Y = 1;

var TIME = 20000;

var drag = null;
var dragEnabled = null;
var dropEnabled = null;

var help = true;
var previousHelpCSS = new Array();
var previousHelpKingCSS = new Array();
var stack = new Array();
var pollInvitation = null;
var invitationID = null

function debugPlayArea() {
    var str = '';
    var index = null;
    var color = null;

    for(var y = 0; y < 8; y ++) {
        str = '';

		for(var x = 0; x < 8; x ++) {
            index = fromXY(x, y);
            color = null
            
            if(playarea[index].color == WHITE) {
                color = 'White';
            }
            if(playarea[index].color == BLACK) {
                color = 'Black';
            }

            str += color + ' ' + playarea[index].name + ' - ';
        }
        
    }
}

function toXY(position) {
	var i = 0;
    
	for(var y = 0; y < 8; y ++) {
		for(var x = 0; x < 8; x ++) {
			if(position == i) {
				return new Array(x, y);
			}
			i ++;
		}
	}
}
				
function fromXY(x, y) {
	var k = 0;
	for(var i = 0; i < 8; i ++) {
		for(var j = 0; j < 8; j ++) {
			if(i == y && j == x) {
				return k;
			}
			k ++;
		}
	}
	return false;
}

function validate(fromIndex, toIndex) {
	var danger = false;
    var tempFromPiece = playarea[fromIndex];
    var tempToPiece = playarea[toIndex];
    
    var kingIndex = getTheKingIndex(tempFromPiece.color);
    
    if(fromIndex == kingIndex) {
        kingIndex = toIndex;
    }
    
    playarea[fromIndex] = new Shape(null, null);
	playarea[toIndex] = tempFromPiece;
    
	if(pieceInDanger(kingIndex)) {
        danger = true;
	}
	
    playarea[fromIndex] = tempFromPiece;
    playarea[toIndex] = tempToPiece;
    
	return danger;
}

function pieceInDanger(pieceIndex) {
    
    if(movePawn(pieceIndex, true)) {
        return true;
    }
    
    if(moveQueen(pieceIndex, true)) {
        return true;
    }
    
    if(moveKnight(pieceIndex, true)) {
        return true;
    }
    
    if(moveKing(pieceIndex, true)) {
        return true;
    }
    
    return false;
}

function inArray(key, array) {
    for(var i = 0; i < array.length; i ++) {
        if(array[i] == key) {
            return true;
        }
    }
    return false;
}

function assignDrop(drop) {
    $.each($('.block'), function(k, v) {
        var index = getBlockIndexFromClass($(v));
        
        if(!$(v).hasClass('ui-droppable') || ($(v).hasClass('ui-droppable') && inArray(index, dropEnabled))) {
            $(v).droppable({accept: '.block img', tolerance: 'intersect', 
                drop: function(event, ui) {
                    var to = getBlockIndexFromClass($(this));
                    var from = getBlockIndexFromClass($(ui.draggable).parent());
                    
                    $(this).html($(ui.draggable));
                    var clone = $(this).clone();
                    
                    if($(ui.draggable).parent().hasClass('uneven')) {
                        $(this).addClass('uneven');
                    } else {
                        $(this).removeClass('uneven');
                    }
                    
                    if(clone.hasClass('uneven')) {
                        $(ui.draggable).parent().addClass('uneven');
                    } else {
                        $(ui.draggable).parent().removeClass('uneven');
                    }
                    
                    $(ui.draggable).attr('style', '');
                    
                    resetZIndex();
                    
                    move = getMove(playarea[from], from, to);
                    
                    playarea[to] = playarea[from];
                    playarea[from] = new Shape(null, null);
                    
                    dragEnabled = new Array();
                    assignDrag();
                        
                    $.ajax({
                        url: 'move?pk=' + invitationID + '&move=' + move + '&from=' + from + '&to=' + to,
                        dataType: 'json',
                        timeout: TIME,
                        method: 'get',
                        cache: false
                    }).done(function(data) {
                        var temp = playarea[data['toXY']];
                        
                        playarea[data['toXY']] = playarea[data['fromXY']];
                        playarea[data['fromXY']] = temp;
                        
                        var temp = $('.block_' + data['toXY']).html();
                        $('.block_' + data['toXY']).html($('.block_' + data['fromXY']).html());
                        $('.block_' + data['fromXY']).html('');
                        
                        setTimeout('setNewDraggables()', 100)
                    }).fail(function(data) {
                        $('#log').show();
                        $('#users').show();
                    })
                }
            });
            try {
                $(v).droppable('option', 'disabled', false);
            } catch(e) {}
        } else {
            try {
                $(v).droppable('option', 'disabled', true);
            } catch(e) {}
        }
    });
}

function setNewDraggables() {
    var kingIndex = getTheKingIndex(currentColor);
    
    if(previousHelpKingCSS.length > 0) {
        $('.block_' + previousHelpKingCSS[0]).css('background-color', previousHelpKingCSS[1])
    }
    
    if(pieceInDanger(kingIndex)) {
        previousHelpKingCSS = new Array();
        if(help) {
            previousHelpKingCSS.push(kingIndex);
            previousHelpKingCSS.push($('.block_' + kingIndex).css('background-color'));
        }
        
        $('.block_' + kingIndex).css('background-color', 'red');
    }

    getActivePiecesAsString();
    assignDrag();
}
                
function getMove(fromObj, from, to) {
    var color = fromObj.color == WHITE ? 'White': 'Black';
    
    return color + ' ' + fromObj.name + ' : ' + getChessMove(from, to);
}

function getChessMove(from, to) {
    var y = new Array('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h');
    var x = new Array(1, 2, 3, 4, 5, 6, 7, 8);
    
    var from = toXY(from);
    var to = toXY(to);
    
    return y[from[1]] + '' + x[from[0]] + ' - ' + y[to[1]] + '' + x[to[0]]
}

function getBlockIndexFromClass(element) {
    var array = element.attr('class').split(' ');
    
    for(var i = 0; i < array.length; i ++) {
        var parts = array[i].split('_')
        if(parts.length > 1) {
            return parseInt(parts[1])
        }
    }
}

function assignDrag() {
    $.each($('.block img'), function(k, v) {
        var index = getBlockIndexFromClass($(v).parent());
        
        if(!$(v).hasClass('ui-draggable') || ($(v).hasClass('ui-draggable') && inArray(index, dragEnabled))) {
            $(v).css('cursor', 'move');
            
            $(v).draggable({cursor: 'move', revert: true, containment: '.container',
                start: function(event, ui) {
                    $(this).parent().css({'z-index': 1});
                    
                    var blockIndex = getBlockIndexFromClass($(this).parent());
                    var block = playarea[blockIndex];
                    
                    
                    previousHelpCSS = new Array();
                        
                    dropEnabled = new Array();
                    var drop = eval('move' + block.name + '(blockIndex, false);');
                    
                    if(drop != '') {
                        drop = drop.substring(0, drop.length - 2)
                        if(help) {
                            $(drop).css('background-color', 'green');
                        }
                        stack.push(previousHelpCSS);
                        assignDrop(drop);
                    }
                },
                stop: function(event, ui) {
                    if(help) {
                        if(stack.length > 0) {
                            for(var i = 0; i < stack[0].length; i ++) {
                                $('.block_' + stack[0][i][0]).css('background-color', stack[0][i][1]);
                            }
                        }
                    }
                    stack.shift();
                }
            });
            try {
                $(v).draggable('option', 'disabled', false);
            } catch(e) {}
        } else {
            try {
                $(v).draggable('option', 'disabled', true);
            } catch(e) {}
        }
    });
}

function resetZIndex() {
    for(var i = 0; i < playarea.length; i ++) {
        $('.block_' + i).css('z-index', 0);
    }
}

function getActivePiecesAsString() {
    drag = '';
    dragEnabled = new Array();
    
    for(var i = 0; i < playarea.length; i ++) {
        if(playarea[i].color == currentColor) {
            dragEnabled.push(i);
            drag += '.block_' + i + ' img, ';
        }
    }
    
    drag = drag.substring(0, drag.length - 2);
}

function getTheKingIndex(color) {
    for(var i = 0; i < playarea.length; i ++) {
        if(playarea[i].color == color && playarea[i].name == KING) {
            return i;
        }
    }
}

function initPlayArea() {
    playarea[0] = new Shape(ROOK, BLACK), playarea[7] = new Shape(ROOK, BLACK);
    playarea[1] = new Shape(KNIGHT, BLACK), playarea[6] = new Shape(KNIGHT, BLACK);
    playarea[2] = new Shape(BISHOP, BLACK), playarea[5] = new Shape(BISHOP, BLACK);
    playarea[3] = new Shape(QUEEN, BLACK);
    playarea[4] = new Shape(KING, BLACK);
    
    for(var i = 8; i < 16; i ++) {
        playarea[i] = new Shape(PAWN, BLACK);
    }
    
    for(var i = 16; i < 48; i ++) {
        playarea[i] = new Shape(null, null);
    }
    
    playarea[56] = new Shape(ROOK, WHITE), playarea[63] = new Shape(ROOK, WHITE);
    playarea[57] = new Shape(KNIGHT, WHITE), playarea[62] = new Shape(KNIGHT, WHITE);
    playarea[58] = new Shape(BISHOP, WHITE), playarea[61] = new Shape(BISHOP, WHITE);
    playarea[59] = new Shape(QUEEN, WHITE);
    playarea[60] = new Shape(KING, WHITE);
    
    for(var i = 48; i < 56; i ++) {
        playarea[i] = new Shape(PAWN, WHITE);
    }
}

$(document).ready(function() {
    currentColor = WHITE;
    initPlayArea();
    
    $(document).on('click', '.invite', function() {
        $('#users').hide();
        
        $.ajax({
            url: 'invite?to_user=' + $(this).text(),
            dataType: 'json',
            method: 'get',
            timeout: TIME,
            cache: false
        }).done(function(data) {
            invitationID = data['pk'];
            $.ajax({
                url: '/chess/move?pk=' + data['pk'],
                dataType: 'json',
                method: 'get',
                timeout: TIME,
                cache: false
            }).done(function(data) {
                var temp = playarea[data['toXY']];
                        
                playarea[data['toXY']] = playarea[data['fromXY']];
                playarea[data['fromXY']] = temp;
                
                var temp = $('.block_' + data['toXY']).html();
                $('.block_' + data['toXY']).html($('.block_' + data['fromXY']).html());
                $('.block_' + data['fromXY']).html('');
                
                currentColor = BLACK;
                getActivePiecesAsString();
                assignDrag(); 
            });
        }).fail(function(data) {
            $('#users').show();
        });
    });
    
    pollInvitations();
    
    var pollInvitation = setInterval('pollInvitations()', 5000);
    
    $(document).on('click', '.accept', function() {
        var link = $(this);
        
        $.ajax({
            url: $(this).attr('href'),
            dataType: 'json',
            method: 'get',
            timeout: TIME,
            cache: false
        }).done(function(data) {
            invitationID = data['invitation'];
            $('#users').hide();
            $('#log').hide();
            
            link.parent().remove();
                        
            getActivePiecesAsString();
            assignDrag(); 
        });
        
        return false;
    });
    
    $(document).on('click', '.reject', function() {
        var link = $(this);
        
        $.ajax({
            url: $(this).attr('href'),
            dataType: 'json',
            method: 'get',
            timeout: TIME,
            cache: false
        }).done(function(data) {
            $('#users').show();
            link.parent().remove();
        });
        
        return false;
    });
});

function pollInvitations() {
    $.ajax({
        url: 'invite-list?direction=to',
        dataType: 'json',
        method: 'get',
        timeout: TIME,
        cache: false
    }).done(function(data) {
        var invitations = data['invitations'];
        
        if(invitations.length > 0) {
            $('#users').hide();
        }
        
        $('#log ul').html('');
        
        $.each(invitations, function(k, v) {
            $('#users').hide();
            $('#log ul').append('<li>' + v[1] + ' has challenged you! <a class="accept" href="/chess/accept-or-reject?accept=1&pk=' + v[0] + '">Accept</a> <a class="reject" href="/chess/accept-or-reject?reject=1&pk=' + v[0] + '">Reject</a></li>');
        });
    }).fail(function(data) {
        $('#users').show();
    })
}