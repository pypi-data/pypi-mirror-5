
define(function(){
  var S4 = function ()
  {
    return Math.floor(
      Math.random() * 0x10000 /* 65536 */
    ).toString(16);
  };

  function GUID (){

    return (
      S4() + S4() + "-" +
	S4() + "-" +
	S4() + "-" +
	S4() + "-" +
	S4() + S4() + S4()
    );
  };

  return GUID;
});